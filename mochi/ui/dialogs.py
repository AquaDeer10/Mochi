"""猫咪信息 / 事件录入对话框。"""
from __future__ import annotations

import shutil
import uuid
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk

from ..age_utils import (
    age_year_month,
    date_from_weeks,
    date_from_year_month,
)
from ..models import Cat, Event, PHOTO_DIR
from .widgets import REPEAT_LABEL_BY_UNIT, REPEAT_UNIT_LABELS, DatePicker

# 常用事件名称快捷选项，按 kind 区分
QUICK_TITLES = {
    "past": [
        "驱虫", "疫苗", "洗澡", "体检",
        "剪指甲", "称体重", "绝育", "看医生",
    ],
    "future": [
        "驱虫", "疫苗", "洗澡", "体检",
        "剪指甲", "称体重", "绝育", "看医生",
    ],
}


class EventDialog(ctk.CTkToplevel):
    def __init__(self, master, cat: Cat, kind: str, on_save,
                 event: Optional[Event] = None):
        super().__init__(master)
        # 先隐藏窗口，等所有子控件创建并应用主题色后再显示，
        # 可消除 CTkToplevel 首帧白闪。
        self.withdraw()
        action = "编辑" if event else "添加"
        scope = "历史事件" if kind == "past" else "未来计划"
        self.title(f"{action}{scope}")
        self.geometry("460x620" if kind == "future" else "460x520")
        self.resizable(False, False)
        self.cat = cat
        self.kind = kind
        self.on_save = on_save
        self.event = event
        self.transient(master)

        pad = {"padx": 16, "pady": 6}

        ctk.CTkLabel(self, text="事件名称").pack(anchor="w", **pad)
        self.entry_title = ctk.CTkEntry(self, placeholder_text="例：第一次驱虫")
        self.entry_title.pack(fill="x", padx=16)
        if event:
            self.entry_title.insert(0, event.title)

        # 快捷填充：点击后替换名称输入框内容
        quick_wrap = ctk.CTkFrame(self, fg_color="transparent")
        quick_wrap.pack(fill="x", padx=16, pady=(6, 0))
        titles = QUICK_TITLES.get(kind, [])
        for i, t in enumerate(titles):
            r, c = divmod(i, 4)
            quick_wrap.grid_columnconfigure(c, weight=1, uniform="qk")
            ctk.CTkButton(
                quick_wrap, text=t, height=26,
                fg_color="transparent", border_width=1,
                text_color=("gray25", "gray85"),
                hover_color=("#e5e7eb", "#333333"),
                command=lambda v=t: self._fill_title(v),
            ).grid(row=r, column=c, padx=2, pady=2, sticky="ew")

        ctk.CTkLabel(self, text="录入方式").pack(anchor="w", **pad)
        self.mode = ctk.StringVar(value="date")
        seg = ctk.CTkSegmentedButton(
            self, values=["按日期", "按周龄", "按年月龄"],
            command=self._on_mode_change,
        )
        seg.set("按日期")
        seg.pack(fill="x", padx=16)
        self._seg = seg

        # 输入区容器
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=16, pady=8)

        # 周期重复（仅未来计划）
        if kind == "future":
            self.repeat_var = ctk.BooleanVar(
                value=bool(event and event.has_repeat()))
            self.repeat_value = ctk.StringVar(
                value=str(event.repeat_value) if (event and event.has_repeat()) else "1")
            init_label = REPEAT_LABEL_BY_UNIT.get(
                event.repeat_unit if event else "", "月")
            self.repeat_unit = ctk.StringVar(value=init_label)

            rep_wrap = ctk.CTkFrame(self, fg_color="transparent")
            rep_wrap.pack(fill="x", padx=16, pady=(8, 0))
            ctk.CTkCheckBox(rep_wrap, text="周期重复",
                            variable=self.repeat_var,
                            command=self._toggle_repeat).pack(anchor="w")

            self.repeat_row = ctk.CTkFrame(self, fg_color="transparent")
            self.repeat_row.pack(fill="x", padx=16, pady=(4, 0))
            ctk.CTkLabel(self.repeat_row, text="每").pack(side="left")
            self.ent_repeat = ctk.CTkEntry(
                self.repeat_row, width=70, textvariable=self.repeat_value)
            self.ent_repeat.pack(side="left", padx=6)
            self.cb_repeat = ctk.CTkComboBox(
                self.repeat_row, width=80,
                values=[lab for lab, _ in REPEAT_UNIT_LABELS],
                variable=self.repeat_unit, state="readonly",
            )
            self.cb_repeat.pack(side="left")
            self._toggle_repeat()

        # 备注
        ctk.CTkLabel(self, text="备注").pack(anchor="w", **pad)
        self.entry_note = ctk.CTkTextbox(self, height=70)
        self.entry_note.pack(fill="x", padx=16)
        if event and event.note:
            self.entry_note.insert("1.0", event.note)

        # 按钮
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=14)
        ctk.CTkButton(btn_row, text="取消", fg_color="gray",
                      command=self.destroy).pack(side="right", padx=4)
        ctk.CTkButton(btn_row, text="保存", command=self._save).pack(side="right", padx=4)

        self._build_inputs("date")
        # 让 Tk 完成所有几何/主题计算后再显示，避免白闪
        self.update_idletasks()
        self.after(10, self._show)

    def _show(self):
        self.deiconify()
        self.grab_set()
        self.focus_force()

    def _toggle_repeat(self):
        state = "normal" if self.repeat_var.get() else "disabled"
        self.ent_repeat.configure(state=state)
        self.cb_repeat.configure(state="readonly" if self.repeat_var.get() else "disabled")

    def _fill_title(self, value: str):
        self.entry_title.delete(0, "end")
        self.entry_title.insert(0, value)
        self.entry_title.focus_set()

    def _on_mode_change(self, value):
        m = {"按日期": "date", "按周龄": "weeks", "按年月龄": "ym"}[value]
        self.mode.set(m)
        self._build_inputs(m)

    def _build_inputs(self, mode: str):
        self.input_frame.update_idletasks()
        for w in self.input_frame.winfo_children():
            w.destroy()
        birth = self.cat.birth()
        cur_date = self.event.as_date() if self.event else date.today()
        if mode == "date":
            self.dp = DatePicker(self.input_frame, initial=cur_date)
            self.dp.pack(anchor="w")
        elif mode == "weeks":
            total = (cur_date - birth).days
            if self.event:
                w_init, wd_init = divmod(abs(total), 7)
                if total < 0:
                    w_init = -w_init
            else:
                w_init, wd_init = 8, 0
            row = ctk.CTkFrame(self.input_frame, fg_color="transparent")
            row.pack(anchor="w")
            self.var_w = ctk.StringVar(value=str(w_init))
            self.var_wd = ctk.StringVar(value=str(wd_init))
            ctk.CTkEntry(row, width=70, textvariable=self.var_w).pack(side="left")
            ctk.CTkLabel(row, text=" 周 ").pack(side="left")
            ctk.CTkEntry(row, width=70, textvariable=self.var_wd).pack(side="left")
            ctk.CTkLabel(row, text=" 天").pack(side="left")
        else:
            if self.event and cur_date >= birth:
                yy, mm, dd = age_year_month(birth, cur_date)
            else:
                yy, mm, dd = 0, 3, 0
            row = ctk.CTkFrame(self.input_frame, fg_color="transparent")
            row.pack(anchor="w")
            self.var_yy = ctk.StringVar(value=str(yy))
            self.var_mm = ctk.StringVar(value=str(mm))
            self.var_dd = ctk.StringVar(value=str(dd))
            ctk.CTkEntry(row, width=60, textvariable=self.var_yy).pack(side="left")
            ctk.CTkLabel(row, text=" 年 ").pack(side="left")
            ctk.CTkEntry(row, width=60, textvariable=self.var_mm).pack(side="left")
            ctk.CTkLabel(row, text=" 月 ").pack(side="left")
            ctk.CTkEntry(row, width=60, textvariable=self.var_dd).pack(side="left")
            ctk.CTkLabel(row, text=" 天").pack(side="left")

    def _resolve_date(self) -> Optional[date]:
        m = self.mode.get()
        birth = self.cat.birth()
        try:
            if m == "date":
                return self.dp.get_date()
            if m == "weeks":
                return date_from_weeks(birth, int(self.var_w.get()), int(self.var_wd.get() or 0))
            return date_from_year_month(birth, int(self.var_yy.get() or 0),
                                        int(self.var_mm.get() or 0),
                                        int(self.var_dd.get() or 0))
        except Exception as e:
            messagebox.showerror("错误", f"日期无效：{e}", parent=self)
            return None

    def _save(self):
        title = self.entry_title.get().strip()
        if not title:
            messagebox.showwarning("提示", "请填写事件名称", parent=self)
            return
        d = self._resolve_date()
        if d is None:
            return
        note = self.entry_note.get("1.0", "end").strip()
        rv, ru = 0, ""
        if self.kind == "future" and self.repeat_var.get():
            try:
                rv = int(self.repeat_value.get())
            except ValueError:
                rv = 0
            if rv <= 0:
                messagebox.showwarning("提示", "周期数值需大于 0", parent=self)
                return
            ru = dict(REPEAT_UNIT_LABELS).get(self.repeat_unit.get(), "")
        if self.event:
            self.event.title = title
            self.event.event_date = d.isoformat()
            self.event.note = note
            self.event.repeat_value = rv
            self.event.repeat_unit = ru
            ev = self.event
        else:
            ev = Event(
                id=uuid.uuid4().hex,
                title=title,
                event_date=d.isoformat(),
                kind=self.kind,
                note=note,
                repeat_value=rv,
                repeat_unit=ru,
            )
        self.on_save(ev)
        self.destroy()


class CatDialog(ctk.CTkToplevel):
    def __init__(self, master, on_save, cat: Optional[Cat] = None):
        super().__init__(master)
        # 同 EventDialog：先隐藏，布局完成后再显示，消除白闪
        self.withdraw()
        self.title("猫咪信息")
        self.geometry("420x360")
        self.resizable(False, False)
        self.on_save = on_save
        self.cat = cat
        self.photo_path: Optional[str] = cat.photo if cat else None
        self.transient(master)

        ctk.CTkLabel(self, text="名称").pack(anchor="w", padx=16, pady=(16, 4))
        self.entry_name = ctk.CTkEntry(self, placeholder_text="给小猫起个名字")
        self.entry_name.pack(fill="x", padx=16)
        if cat:
            self.entry_name.insert(0, cat.name)

        ctk.CTkLabel(self, text="出生日期").pack(anchor="w", padx=16, pady=(12, 4))
        self.dp = DatePicker(self, initial=cat.birth() if cat else date.today())
        self.dp.pack(anchor="w", padx=16)

        ctk.CTkLabel(self, text="照片").pack(anchor="w", padx=16, pady=(12, 4))
        photo_row = ctk.CTkFrame(self, fg_color="transparent")
        photo_row.pack(fill="x", padx=16)
        self.lbl_photo = ctk.CTkLabel(
            photo_row,
            text=self.photo_path if self.photo_path else "未选择",
            anchor="w",
        )
        self.lbl_photo.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(photo_row, text="选择…", width=80,
                      command=self._pick_photo).pack(side="right")

        btn = ctk.CTkFrame(self, fg_color="transparent")
        btn.pack(fill="x", padx=16, pady=20)
        ctk.CTkButton(btn, text="取消", fg_color="gray",
                      command=self.destroy).pack(side="right", padx=4)
        ctk.CTkButton(btn, text="保存", command=self._save).pack(side="right", padx=4)

        self.update_idletasks()
        self.after(10, self._show)

    def _show(self):
        self.deiconify()
        self.grab_set()
        self.focus_force()

    def _pick_photo(self):
        f = filedialog.askopenfilename(
            title="选择照片",
            filetypes=[("图像", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")],
            parent=self,
        )
        if f:
            self.photo_path = f
            self.lbl_photo.configure(text=Path(f).name)

    def _save(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("提示", "请填写名称", parent=self)
            return
        try:
            birth = self.dp.get_date()
        except Exception:
            messagebox.showerror("错误", "出生日期无效", parent=self)
            return
        if birth > date.today():
            messagebox.showwarning("提示", "出生日期不能晚于今天", parent=self)
            return

        photo_name = self.cat.photo if self.cat else ""
        if self.photo_path and (not self.cat or self.photo_path != self.cat.photo):
            src = Path(self.photo_path)
            if src.is_file():
                ext = src.suffix.lower() or ".png"
                photo_name = f"{uuid.uuid4().hex}{ext}"
                shutil.copyfile(src, PHOTO_DIR / photo_name)

        if self.cat:
            self.cat.name = name
            self.cat.birth_date = birth.isoformat()
            self.cat.photo = photo_name
            self.on_save(self.cat)
        else:
            cat = Cat(id=uuid.uuid4().hex, name=name,
                      birth_date=birth.isoformat(), photo=photo_name)
            self.on_save(cat)
        self.destroy()
