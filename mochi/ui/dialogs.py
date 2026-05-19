"""猫咪信息 / 事件录入对话框。"""
from __future__ import annotations

import shutil
import uuid
from datetime import date
from pathlib import Path
from tkinter import Canvas, filedialog, messagebox
from typing import Optional

import customtkinter as ctk

from ..age_utils import (
    age_year_month,
    date_from_weeks,
    date_from_year_month,
)
from .layout_constants import *
from ..models import Cat, Event, PHOTO_DIR, WeightRecord
from .widgets import REPEAT_LABEL_BY_UNIT, REPEAT_UNIT_LABELS, DatePicker

# 常用事件名称快捷选项，按 kind 区分
QUICK_TITLES = {
    "past": [
        "内驱", "外驱", "疫苗", "洗澡", "体检",
        "剪指甲", "绝育", "看医生",
    ],
    "future": [
        "内驱", "外驱", "疫苗", "洗澡", "体检",
        "剪指甲", "绝育", "看医生",
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
        self.geometry(
            f"{EVENT_DIALOG_WIDTH}x{EVENT_DIALOG_FUTURE_HEIGHT}"
            if kind == "future"
            else f"{EVENT_DIALOG_WIDTH}x{EVENT_DIALOG_PAST_HEIGHT}"
        )
        self.resizable(False, False)
        self.cat = cat
        self.kind = kind
        self.on_save = on_save
        self.event = event
        self.transient(master)

        pad = {"padx": DIALOG_SIDE_PAD, "pady": DIALOG_LABEL_PADY}

        ctk.CTkLabel(self, text="事件名称").pack(anchor="w", **pad)
        self.entry_title = ctk.CTkEntry(self, placeholder_text="例：第一次驱虫")
        self.entry_title.pack(fill="x", padx=DIALOG_SIDE_PAD)
        if event:
            self.entry_title.insert(0, event.title)

        # 快捷填充：点击后替换名称输入框内容
        quick_wrap = ctk.CTkFrame(self, fg_color="transparent")
        quick_wrap.pack(fill="x", padx=DIALOG_SIDE_PAD, pady=EVENT_TITLE_QUICK_PADY)
        titles = QUICK_TITLES.get(kind, [])
        for i, t in enumerate(titles):
            r, c = divmod(i, 4)
            quick_wrap.grid_columnconfigure(c, weight=1, uniform="qk")
            ctk.CTkButton(
                quick_wrap, text=t, height=EVENT_QUICK_BTN_HEIGHT,
                fg_color="transparent", border_width=BORDER_THIN,
                text_color=("gray25", "gray85"),
                hover_color=("#e5e7eb", "#333333"),
                command=lambda v=t: self._fill_title(v),
            ).grid(row=r, column=c, padx=EVENT_QUICK_BTN_PAD, pady=EVENT_QUICK_BTN_PAD, sticky="ew")

        ctk.CTkLabel(self, text="录入方式").pack(anchor="w", **pad)
        self.mode = ctk.StringVar(value="date")
        seg = ctk.CTkSegmentedButton(
            self, values=["按日期", "按周龄", "按年月龄"],
            command=self._on_mode_change,
        )
        seg.set("按日期")
        seg.pack(fill="x", padx=DIALOG_SIDE_PAD)
        self._seg = seg

        # 输入区容器
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=DIALOG_SIDE_PAD, pady=EVENT_INPUT_PADY)

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
            rep_wrap.pack(fill="x", padx=DIALOG_SIDE_PAD, pady=EVENT_REPEAT_WRAP_PADY)
            ctk.CTkCheckBox(rep_wrap, text="周期重复",
                            variable=self.repeat_var,
                            command=self._toggle_repeat).pack(anchor="w")

            self.repeat_row = ctk.CTkFrame(self, fg_color="transparent")
            self.repeat_row.pack(fill="x", padx=DIALOG_SIDE_PAD, pady=EVENT_REPEAT_ROW_PADY)
            ctk.CTkLabel(self.repeat_row, text="每").pack(side="left")
            self.ent_repeat = ctk.CTkEntry(
                self.repeat_row, width=EVENT_REPEAT_VALUE_WIDTH, textvariable=self.repeat_value)
            self.ent_repeat.pack(side="left", padx=EVENT_REPEAT_VALUE_PADX)
            self.cb_repeat = ctk.CTkComboBox(
                self.repeat_row, width=EVENT_REPEAT_UNIT_WIDTH,
                values=[lab for lab, _ in REPEAT_UNIT_LABELS],
                variable=self.repeat_unit, state="readonly",
            )
            self.cb_repeat.pack(side="left")
            self._toggle_repeat()

        # 备注
        ctk.CTkLabel(self, text="备注").pack(anchor="w", **pad)
        self.entry_note = ctk.CTkTextbox(self, height=EVENT_NOTE_HEIGHT)
        self.entry_note.pack(fill="x", padx=DIALOG_SIDE_PAD)
        if event and event.note:
            self.entry_note.insert("1.0", event.note)

        # 按钮
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=DIALOG_SIDE_PAD, pady=EVENT_BUTTON_ROW_PADY)
        ctk.CTkButton(btn_row, text="取消", fg_color="gray",
                      command=self.destroy).pack(side="right", padx=EVENT_BUTTON_PADX)
        ctk.CTkButton(btn_row, text="保存", command=self._save).pack(side="right", padx=EVENT_BUTTON_PADX)

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
            ctk.CTkEntry(row, width=EVENT_WEEK_INPUT_WIDTH, textvariable=self.var_w).pack(side="left")
            ctk.CTkLabel(row, text=" 周 ").pack(side="left")
            ctk.CTkEntry(row, width=EVENT_WEEK_INPUT_WIDTH, textvariable=self.var_wd).pack(side="left")
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
            ctk.CTkEntry(row, width=EVENT_YM_INPUT_WIDTH, textvariable=self.var_yy).pack(side="left")
            ctk.CTkLabel(row, text=" 年 ").pack(side="left")
            ctk.CTkEntry(row, width=EVENT_YM_INPUT_WIDTH, textvariable=self.var_mm).pack(side="left")
            ctk.CTkLabel(row, text=" 月 ").pack(side="left")
            ctk.CTkEntry(row, width=EVENT_YM_INPUT_WIDTH, textvariable=self.var_dd).pack(side="left")
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
        self.geometry(CAT_DIALOG_GEOMETRY)
        self.resizable(False, False)
        self.on_save = on_save
        self.cat = cat
        self.photo_path: Optional[str] = cat.photo if cat else None
        self.transient(master)

        ctk.CTkLabel(self, text="名称").pack(anchor="w", padx=DIALOG_SIDE_PAD, pady=CAT_LABEL_TOP_PADY)
        self.entry_name = ctk.CTkEntry(self, placeholder_text="给小猫起个名字")
        self.entry_name.pack(fill="x", padx=DIALOG_SIDE_PAD)
        if cat:
            self.entry_name.insert(0, cat.name)

        ctk.CTkLabel(self, text="出生日期").pack(anchor="w", padx=DIALOG_SIDE_PAD, pady=CAT_SECTION_PADY)
        self.dp = DatePicker(self, initial=cat.birth() if cat else date.today())
        self.dp.pack(anchor="w", padx=DIALOG_SIDE_PAD)

        ctk.CTkLabel(self, text="照片").pack(anchor="w", padx=DIALOG_SIDE_PAD, pady=CAT_SECTION_PADY)
        photo_row = ctk.CTkFrame(self, fg_color="transparent")
        photo_row.pack(fill="x", padx=DIALOG_SIDE_PAD)
        self.lbl_photo = ctk.CTkLabel(
            photo_row,
            text=self.photo_path if self.photo_path else "未选择",
            anchor="w",
        )
        self.lbl_photo.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(photo_row, text="选择…", width=CAT_PHOTO_BUTTON_WIDTH,
                      command=self._pick_photo).pack(side="right")

        btn = ctk.CTkFrame(self, fg_color="transparent")
        btn.pack(fill="x", padx=DIALOG_SIDE_PAD, pady=CAT_BUTTON_ROW_PADY)
        ctk.CTkButton(btn, text="取消", fg_color="gray",
                      command=self.destroy).pack(side="right", padx=EVENT_BUTTON_PADX)
        ctk.CTkButton(btn, text="保存", command=self._save).pack(side="right", padx=EVENT_BUTTON_PADX)

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


class WeightDialog(ctk.CTkToplevel):
    def __init__(self, master, cat: Cat, on_save):
        super().__init__(master)
        self.withdraw()
        self._chart_after_id = None
        self._chart_size = (0, 0)
        self.title(f"体重管理 · {cat.name}")
        self.geometry(WEIGHT_DIALOG_GEOMETRY)
        self.minsize(WEIGHT_DIALOG_MIN_WIDTH, WEIGHT_DIALOG_MIN_HEIGHT)
        self.cat = cat
        self.on_save = on_save
        self.transient(master)

        chart_wrap = ctk.CTkFrame(self)
        chart_wrap.pack(fill="x", padx=WEIGHT_SECTION_PADX, pady=WEIGHT_CHART_PADY)
        ctk.CTkLabel(
            chart_wrap,
            text="体重趋势图（kg）",
            font=ctk.CTkFont(size=WEIGHT_CHART_TITLE_FONT, weight="bold"),
        ).pack(anchor="w", padx=WEIGHT_CHART_TITLE_PADX, pady=WEIGHT_CHART_TITLE_PADY)
        self.canvas = Canvas(chart_wrap, height=WEIGHT_CANVAS_HEIGHT, highlightthickness=0)
        self.canvas.pack(fill="x", padx=WEIGHT_CANVAS_PADX, pady=WEIGHT_CANVAS_PADY)

        entry_wrap = ctk.CTkFrame(self)
        entry_wrap.pack(fill="x", padx=WEIGHT_SECTION_PADX, pady=WEIGHT_ENTRY_ROW_PADY)
        ctk.CTkLabel(entry_wrap, text="日期").pack(side="left", padx=WEIGHT_ENTRY_LABEL_PADX, pady=WEIGHT_ENTRY_LABEL_PADY)
        self.dp = DatePicker(entry_wrap, initial=date.today())
        self.dp.pack(side="left", padx=WEIGHT_ENTRY_DP_PADX, pady=WEIGHT_ENTRY_DP_PADY)
        ctk.CTkLabel(entry_wrap, text="体重(kg)").pack(side="left", padx=(0, 6))
        self.var_weight = ctk.StringVar()
        self.ent_weight = ctk.CTkEntry(entry_wrap, width=WEIGHT_INPUT_WIDTH, textvariable=self.var_weight)
        self.ent_weight.pack(side="left", padx=WEIGHT_ENTRY_DP_PADX)
        ctk.CTkButton(entry_wrap, text="保存记录", width=WEIGHT_SAVE_BTN_WIDTH,
                  command=self._save_weight).pack(side="left", padx=WEIGHT_SAVE_BTN_PADX)

        list_wrap = ctk.CTkFrame(self)
        list_wrap.pack(fill="both", expand=True, padx=WEIGHT_SECTION_PADX, pady=WEIGHT_LIST_PADY)
        ctk.CTkLabel(
            list_wrap,
            text="记录列表（点击删除可移除）",
            font=ctk.CTkFont(size=WEIGHT_LIST_TITLE_FONT, weight="bold"),
        ).pack(anchor="w", padx=WEIGHT_LIST_TITLE_PADX, pady=WEIGHT_LIST_TITLE_PADY)
        self.list_frame = ctk.CTkScrollableFrame(list_wrap, fg_color="transparent", height=WEIGHT_LIST_HEIGHT)
        self.list_frame.pack(fill="both", expand=True, padx=WEIGHT_LIST_PADX, pady=WEIGHT_CANVAS_PADY)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=WEIGHT_SECTION_PADX, pady=WEIGHT_CLOSE_ROW_PADY)
        ctk.CTkButton(btn_row, text="关闭", fg_color="gray",
                      command=self._close).pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self._close)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._refresh_all()
        self.update_idletasks()
        self.after(10, self._show)

    def _close(self):
        if self._chart_after_id is not None:
            try:
                self.after_cancel(self._chart_after_id)
            except Exception:
                pass
            self._chart_after_id = None
        self.destroy()

    def _on_canvas_configure(self, event):
        size = (event.width, event.height)
        if size == self._chart_size:
            return
        self._chart_size = size
        self._schedule_render_chart()

    def _schedule_render_chart(self):
        # 防抖：拖动窗口时不要每一帧都全量重绘折线图
        if self._chart_after_id is not None:
            try:
                self.after_cancel(self._chart_after_id)
            except Exception:
                pass
        self._chart_after_id = self.after(WEIGHT_CHART_DEBOUNCE_MS, self._render_chart)

    def _show(self):
        self.deiconify()
        self.grab_set()
        self.focus_force()

    def _records(self) -> list[WeightRecord]:
        return sorted(self.cat.weights, key=lambda w: w.record_date)

    def _save_weight(self):
        try:
            d = self.dp.get_date()
        except Exception:
            messagebox.showerror("错误", "日期无效", parent=self)
            return
        try:
            value = float(self.var_weight.get().strip())
        except Exception:
            messagebox.showwarning("提示", "请输入有效体重（如 2.35）", parent=self)
            return
        if value <= 0 or value > 30:
            messagebox.showwarning("提示", "体重范围应在 0~30 kg", parent=self)
            return

        iso = d.isoformat()
        updated = False
        for w in self.cat.weights:
            if w.record_date == iso:
                w.weight_kg = value
                updated = True
                break
        if not updated:
            self.cat.weights.append(WeightRecord(record_date=iso, weight_kg=value))

        self.on_save()
        self.var_weight.set("")
        self._refresh_all()

    def _delete_weight(self, rec: WeightRecord):
        if not messagebox.askyesno("确认", f"删除 {rec.record_date} 的体重记录？", parent=self):
            return
        self.cat.weights = [w for w in self.cat.weights if w.record_date != rec.record_date]
        self.on_save()
        self._refresh_all()

    def _refresh_all(self):
        self._render_chart()
        self._render_list()

    def _render_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        records = list(reversed(self._records()))
        if not records:
            ctk.CTkLabel(self.list_frame, text="暂无体重记录",
                         text_color=("gray50", "gray60")).pack(
                             anchor="w", padx=WEIGHT_EMPTY_LIST_PAD, pady=WEIGHT_RECORD_ROW_PADY
                         )
            return

        for rec in records:
            row = ctk.CTkFrame(self.list_frame, fg_color=("#f8fafc", "#2a2a2a"), corner_radius=WEIGHT_RECORD_ROW_CORNER)
            row.pack(fill="x", padx=WEIGHT_RECORD_ROW_PADX, pady=WEIGHT_RECORD_ROW_PADY)
            ctk.CTkLabel(row, text=rec.record_date, width=WEIGHT_RECORD_DATE_WIDTH,
                         anchor="w").pack(side="left", padx=WEIGHT_RECORD_DATE_PADX, pady=WEIGHT_RECORD_DATE_PADY)
            ctk.CTkLabel(row, text=f"{rec.weight_kg:.2f} kg",
                         anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
            ctk.CTkButton(row, text="删除", width=WEIGHT_RECORD_DELETE_WIDTH, height=WEIGHT_RECORD_DELETE_HEIGHT,
                          fg_color="transparent", border_width=BORDER_THIN,
                          text_color=("#b91c1c", "#fca5a5"),
                          command=lambda r=rec: self._delete_weight(r)
                          ).pack(side="right", padx=WEIGHT_RECORD_DELETE_PADX)

    def _render_chart(self):
        self._chart_after_id = None
        self.canvas.delete("all")
        records = self._records()
        w = max(self.canvas.winfo_width(), CHART_MIN_WIDTH)
        h = max(self.canvas.winfo_height(), CHART_MIN_HEIGHT)
        pad_l, pad_r, pad_t, pad_b = CHART_PAD_LEFT, CHART_PAD_RIGHT, CHART_PAD_TOP, CHART_PAD_BOTTOM
        x0, y0 = pad_l, h - pad_b
        x1, y1 = w - pad_r, pad_t

        # 坐标轴
        axis_color = "#9ca3af"
        self.canvas.create_line(x0, y0, x1, y0, fill=axis_color)
        self.canvas.create_line(x0, y0, x0, y1, fill=axis_color)

        if not records:
            self.canvas.create_text(
                (x0 + x1) / 2,
                (y0 + y1) / 2,
                text="暂无数据，添加后将显示折线图",
                fill="#6b7280",
                font=("Microsoft YaHei", CHART_EMPTY_FONT_SIZE),
            )
            return

        ys = [r.weight_kg for r in records]
        y_min = min(ys)
        y_max = max(ys)
        if abs(y_max - y_min) < 0.05:
            y_min -= 0.2
            y_max += 0.2
        y_pad = max((y_max - y_min) * 0.15, 0.1)
        y_min -= y_pad
        y_max += y_pad

        def sx(i: int) -> float:
            if len(records) == 1:
                return (x0 + x1) / 2
            return x0 + (x1 - x0) * i / (len(records) - 1)

        def sy(v: float) -> float:
            ratio = (v - y_min) / (y_max - y_min)
            return y0 - ratio * (y0 - y1)

        # Y 轴刻度
        for i in range(CHART_AXIS_TICK_COUNT):
            v = y_min + (y_max - y_min) * i / (CHART_AXIS_TICK_COUNT - 1)
            yy = sy(v)
            self.canvas.create_line(x0 - 4, yy, x0, yy, fill=axis_color)
            self.canvas.create_text(x0 - 8, yy, text=f"{v:.1f}", fill="#6b7280",
                                    anchor="e", font=("Microsoft YaHei", CHART_TICK_FONT_SIZE))

        points = []
        for i, rec in enumerate(records):
            x = sx(i)
            y = sy(rec.weight_kg)
            points.extend([x, y])
            if i == 0 or i == len(records) - 1:
                self.canvas.create_text(x, y0 + 14, text=rec.record_date[5:], fill="#6b7280",
                                        font=("Microsoft YaHei", CHART_TICK_FONT_SIZE))

        if len(points) >= 4:
            self.canvas.create_line(*points, fill="#3b82f6", width=CHART_LINE_WIDTH, smooth=True)
        for i, rec in enumerate(records):
            x = sx(i)
            y = sy(rec.weight_kg)
            self.canvas.create_oval(x - CHART_POINT_RADIUS, y - CHART_POINT_RADIUS,
                                    x + CHART_POINT_RADIUS, y + CHART_POINT_RADIUS,
                                    fill="#2563eb", outline="")
            if i == len(records) - 1:
                self.canvas.create_text(x + CHART_LAST_LABEL_OFFSET_X, y - CHART_LAST_LABEL_OFFSET_Y,
                                        text=f"{rec.weight_kg:.2f}kg",
                                        fill="#2563eb", anchor="w",
                                        font=("Microsoft YaHei", CHART_TICK_FONT_SIZE, "bold"))
