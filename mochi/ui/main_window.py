"""主窗口。"""
from __future__ import annotations

import uuid
from datetime import date
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk
from PIL import Image

from ..age_utils import add_offset, age_days, age_weeks, age_year_month
from ..models import Cat, Event, PHOTO_DIR, load_cats, save_cats
from .dialogs import CatDialog, EventDialog
from .widgets import REPEAT_LABEL_BY_UNIT


class App(ctk.CTk):
    def __init__(self):
        # 注意：外观/主题必须在创建 CTk 根窗口之前设置，
        # 否则根窗口会先用默认外观绘制一次再切换，产生启动白闪。
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        super().__init__()
        # 把根窗口背景显式设为当前主题色，避免子控件 destroy/重建瞬间
        # 露出 Tk 默认白底。
        try:
            bg = self._apply_appearance_mode(
                ctk.ThemeManager.theme["CTk"]["fg_color"])
            self.configure(fg_color=bg)
        except Exception:
            pass
        self.title("Mochi · 小猫成长管理")
        self.geometry("1080x680")
        self.minsize(960, 600)

        self.cats: list[Cat] = load_cats()
        self.current: Optional[Cat] = None
        self._photo_cache: dict[str, ctk.CTkImage] = {}

        self._build_ui()
        if self.cats:
            self._select_cat(self.cats[0])
        else:
            self._render_empty()

    # ---------- UI 构建 ----------
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        side = ctk.CTkFrame(self, width=240, corner_radius=0)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)
        side.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            side, text="🐾 我的猫咪",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(20, 10), sticky="w")

        ctk.CTkButton(
            side, text="+ 添加猫咪", height=36,
            command=self._add_cat,
        ).grid(row=1, column=0, padx=16, pady=4, sticky="ew")

        self.cat_list_frame = ctk.CTkScrollableFrame(side, fg_color="transparent")
        self.cat_list_frame.grid(row=2, column=0, padx=8, pady=10, sticky="nsew")

        self.main = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)

        self._refresh_cat_list()

    # ---------- 列表 ----------
    def _refresh_cat_list(self):
        # 暂停重绘，等本帧重建完毕后一次性 flush，避免中途露白
        self.cat_list_frame.update_idletasks()
        for w in self.cat_list_frame.winfo_children():
            w.destroy()
        for cat in self.cats:
            is_cur = self.current and cat.id == self.current.id
            btn = ctk.CTkButton(
                self.cat_list_frame, text=cat.name, height=40, anchor="w",
                fg_color=("#1f6aa5" if is_cur else "transparent"),
                text_color=("white" if is_cur else None),
                hover_color=("#1f6aa5" if is_cur else ("#e0e0e0", "#2b2b2b")),
                command=lambda c=cat: self._select_cat(c),
            )
            btn.pack(fill="x", padx=4, pady=2)

    def _select_cat(self, cat: Cat):
        self.current = cat
        self._refresh_cat_list()
        self._render_detail()

    # ---------- 空状态 ----------
    def _render_empty(self):
        self.main.update_idletasks()
        for w in self.main.winfo_children():
            w.destroy()
        wrap = ctk.CTkFrame(self.main, fg_color="transparent")
        wrap.grid(row=0, column=0, pady=120)
        ctk.CTkLabel(wrap, text="🐱", font=ctk.CTkFont(size=80)).pack()
        ctk.CTkLabel(
            wrap, text="还没有猫咪资料\n点击左侧 “+ 添加猫咪” 开始",
            font=ctk.CTkFont(size=16), justify="center",
        ).pack(pady=12)

    # ---------- 详情卡 ----------
    def _render_detail(self):
        self.main.update_idletasks()
        for w in self.main.winfo_children():
            w.destroy()
        if not self.current:
            self._render_empty()
            return
        cat = self.current

        card = ctk.CTkFrame(self.main, corner_radius=16)
        card.grid(row=0, column=0, padx=24, pady=24, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        photo_widget = self._build_photo(card, cat)
        photo_widget.grid(row=0, column=0, rowspan=2, padx=20, pady=20)

        name_row = ctk.CTkFrame(card, fg_color="transparent")
        name_row.grid(row=0, column=1, sticky="ew", padx=10, pady=(20, 4))
        ctk.CTkLabel(
            name_row, text=cat.name,
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(name_row, text="编辑", width=60, height=28,
                      command=self._edit_cat).pack(side="left", padx=10)
        ctk.CTkButton(name_row, text="删除", width=60, height=28,
                      fg_color="#c0392b", hover_color="#922b21",
                      command=self._delete_cat).pack(side="left")

        birth = cat.birth()
        days = age_days(birth)
        weeks, wd = age_weeks(birth)
        y, m, d = age_year_month(birth)
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=1, column=1, sticky="ew", padx=10, pady=(4, 20))
        self._age_chip(info, "出生日期", birth.strftime("%Y-%m-%d"))
        self._age_chip(info, "天数", f"{days} 天")
        self._age_chip(info, "周龄", f"{weeks} 周 {wd} 天")
        self._age_chip(info, "年月龄", f"{y} 岁 {m} 月 {d} 天")

        self._render_event_section(
            row=1, title="📅 已发生事件", kind="past",
            events=sorted([e for e in cat.events if e.kind == "past"],
                          key=lambda e: e.event_date),
        )
        self._render_event_section(
            row=2, title="🌱 未来计划", kind="future",
            events=sorted([e for e in cat.events if e.kind == "future"],
                          key=lambda e: e.event_date),
        )

    def _age_chip(self, parent, label, value):
        chip = ctk.CTkFrame(parent, corner_radius=10)
        chip.pack(side="left", padx=(0, 10), pady=4)
        ctk.CTkLabel(chip, text=label, font=ctk.CTkFont(size=11),
                     text_color=("gray40", "gray70")).pack(padx=12, pady=(8, 0))
        ctk.CTkLabel(chip, text=value,
                     font=ctk.CTkFont(size=15, weight="bold")).pack(padx=12, pady=(0, 8))

    def _build_photo(self, parent, cat: Cat):
        size = 140
        if cat.photo and (PHOTO_DIR / cat.photo).is_file():
            try:
                img = Image.open(PHOTO_DIR / cat.photo).convert("RGBA")
                img.thumbnail((size * 2, size * 2))
                ck = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
                self._photo_cache[cat.id] = ck
                return ctk.CTkLabel(parent, image=ck, text="")
            except Exception:
                pass
        return ctk.CTkLabel(
            parent, text="🐱", width=size, height=size,
            font=ctk.CTkFont(size=72),
            fg_color=("#f0f0f0", "#2b2b2b"), corner_radius=12,
        )

    def _render_event_section(self, row, title, kind, events):
        cat = self.current
        sec = ctk.CTkFrame(self.main, corner_radius=16)
        sec.grid(row=row, column=0, padx=24, pady=(0, 16), sticky="ew")
        sec.grid_columnconfigure(0, weight=1)

        head = ctk.CTkFrame(sec, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=16, pady=12)
        head.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(head, text=title,
                     font=ctk.CTkFont(size=18, weight="bold")
                     ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(head, text="+ 添加", width=80,
                      command=lambda k=kind: self._add_event(k)
                      ).grid(row=0, column=1, sticky="e")

        if not events:
            ctk.CTkLabel(
                sec, text="（暂无）",
                text_color=("gray50", "gray60"),
            ).grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")
            return

        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 12))
        body.grid_columnconfigure(0, weight=1)
        assert cat is not None
        for i, ev in enumerate(events):
            self._render_event_row(body, i, ev, cat)

    def _render_event_row(self, parent, idx, ev: Event, cat: Cat):
        row = ctk.CTkFrame(parent, corner_radius=10,
                           fg_color=("#f7f7f7", "#2b2b2b"))
        row.grid(row=idx, column=0, sticky="ew", padx=8, pady=4)
        row.grid_columnconfigure(1, weight=1)

        d = ev.as_date()
        birth = cat.birth()
        days = (d - birth).days
        sign = "-" if days < 0 else ""
        ad = abs(days)
        wks, wd = divmod(ad, 7)
        if days >= 0:
            y, m, dd = age_year_month(birth, d)
            ym_text = f"{y}岁{m}月{dd}天"
        else:
            y, m, dd = age_year_month(d, birth)
            ym_text = f"-{y}岁{m}月{dd}天"
        sub = (f"{d.strftime('%Y-%m-%d')}  ·  "
               f"{sign}{ad}天  ·  {sign}{wks}周{wd}天  ·  {ym_text}")
        if ev.kind == "future":
            delta = (d - date.today()).days
            sub += f"  ·  距今 {delta} 天" if delta >= 0 else f"  ·  已过 {-delta} 天"
        if ev.has_repeat():
            sub += f"  ·  🔁 每 {ev.repeat_value} {REPEAT_LABEL_BY_UNIT.get(ev.repeat_unit, '')}"

        ctk.CTkLabel(row, text=ev.title,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     anchor="w").grid(row=0, column=0, columnspan=2,
                                      padx=14, pady=(10, 2), sticky="w")
        ctk.CTkLabel(row, text=sub, anchor="w",
                     text_color=("gray40", "gray70")
                     ).grid(row=1, column=0, padx=14, pady=(0, 2), sticky="w")
        if ev.note:
            ctk.CTkLabel(row, text=ev.note, anchor="w", justify="left",
                         wraplength=600
                         ).grid(row=2, column=0, columnspan=2,
                                padx=14, pady=(0, 8), sticky="w")
        else:
            ctk.CTkFrame(row, fg_color="transparent", height=6
                         ).grid(row=2, column=0)

        btns = ctk.CTkFrame(row, fg_color="transparent")
        btns.grid(row=0, column=1, padx=10, sticky="e")
        if ev.kind == "future":
            ctk.CTkButton(btns, text="完成", width=60, height=26,
                          fg_color="#27ae60", hover_color="#1e8449",
                          command=lambda e=ev: self._complete_event(e)
                          ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(btns, text="编辑", width=60, height=26,
                      fg_color="transparent", border_width=1,
                      text_color=("gray30", "gray80"),
                      command=lambda e=ev: self._edit_event(e)
                      ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(btns, text="删除", width=60, height=26,
                      fg_color="transparent", border_width=1,
                      text_color=("gray30", "gray80"),
                      command=lambda e=ev: self._delete_event(e)
                      ).pack(side="left")

    # ---------- 操作 ----------
    def _add_cat(self):
        CatDialog(self, on_save=self._on_cat_saved)

    def _edit_cat(self):
        if self.current:
            CatDialog(self, on_save=self._on_cat_saved, cat=self.current)

    def _on_cat_saved(self, cat: Cat):
        if cat not in self.cats:
            self.cats.append(cat)
        save_cats(self.cats)
        self._select_cat(cat)

    def _delete_cat(self):
        if not self.current:
            return
        if not messagebox.askyesno("确认", f"删除「{self.current.name}」及其所有事件？"):
            return
        self.cats = [c for c in self.cats if c.id != self.current.id]
        save_cats(self.cats)
        self.current = self.cats[0] if self.cats else None
        self._refresh_cat_list()
        if self.current:
            self._render_detail()
        else:
            self._render_empty()

    def _add_event(self, kind: str):
        if not self.current:
            return
        EventDialog(self, cat=self.current, kind=kind, on_save=self._on_event_saved)

    def _edit_event(self, ev: Event):
        if not self.current:
            return
        EventDialog(self, cat=self.current, kind=ev.kind,
                    on_save=self._on_event_saved, event=ev)

    def _complete_event(self, ev: Event):
        if not self.current or ev.kind != "future":
            return
        today = date.today()
        if ev.has_repeat():
            next_date = add_offset(today, ev.repeat_value, ev.repeat_unit)
            self.current.events.append(Event(
                id=uuid.uuid4().hex,
                title=ev.title,
                event_date=next_date.isoformat(),
                kind="future",
                note=ev.note,
                repeat_value=ev.repeat_value,
                repeat_unit=ev.repeat_unit,
            ))
        ev.kind = "past"
        ev.event_date = today.isoformat()
        ev.repeat_value = 0
        ev.repeat_unit = ""
        save_cats(self.cats)
        self._render_detail()

    def _on_event_saved(self, ev: Event):
        if not self.current:
            return
        if ev not in self.current.events:
            self.current.events.append(ev)
        save_cats(self.cats)
        self._render_detail()

    def _delete_event(self, ev: Event):
        if not self.current:
            return
        if not messagebox.askyesno("确认", f"删除事件「{ev.title}」？"):
            return
        self.current.events = [e for e in self.current.events if e.id != ev.id]
        save_cats(self.cats)
        self._render_detail()
