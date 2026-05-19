"""主窗口。"""
from __future__ import annotations

import uuid
from datetime import date
from pathlib import Path
from tkinter import messagebox
from typing import Any, Optional
import os
import subprocess
import sys

import customtkinter as ctk
from PIL import Image

from ..age_utils import add_offset, age_days, age_weeks, age_year_month
from ..models import Cat, Event, PHOTO_DIR, app_dir, load_cats, save_cats
from .dialogs import CatDialog, EventDialog, WeightDialog
from .layout_constants import *
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
        self.geometry(APP_GEOMETRY)
        self.minsize(APP_MIN_WIDTH, APP_MIN_HEIGHT)

        self.cats: list[Cat] = load_cats()
        self.current: Optional[Cat] = None
        self._photo_cache: dict[str, ctk.CTkImage] = {}
        self.event_scroller: Optional[ctk.CTkScrollableFrame] = None
        self.event_sections: Optional[ctk.CTkFrame] = None
        self._event_section_views: dict[str, dict[str, Any]] = {}
        self._data_dir = app_dir()

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        if self.cats:
            self._select_cat(self.cats[0])
        else:
            self._render_empty()

    # ---------- UI 构建 ----------
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        side = ctk.CTkFrame(self, width=SIDE_WIDTH, corner_radius=RADIUS_NONE)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)
        side.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            side, text="🐾 我的猫咪",
            font=ctk.CTkFont(size=TITLE_FONT_SIZE, weight="bold"),
        ).grid(row=0, column=0, padx=SIDE_TITLE_PADX, pady=SIDE_TITLE_PADY, sticky="w")

        ctk.CTkButton(
            side, text="+ 添加猫咪", height=ADD_CAT_BTN_HEIGHT,
            command=self._add_cat,
        ).grid(row=1, column=0, padx=SIDE_ADD_PADX, pady=SIDE_ADD_PADY, sticky="ew")

        self.cat_list_frame = ctk.CTkScrollableFrame(side, fg_color="transparent")
        self.cat_list_frame.grid(row=2, column=0, padx=CAT_LIST_PADX, pady=CAT_LIST_PADY, sticky="nsew")

        self.main = ctk.CTkFrame(self, corner_radius=RADIUS_NONE)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

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
                self.cat_list_frame, text=cat.name, height=CAT_ITEM_HEIGHT, anchor="w",
                fg_color=("#1f6aa5" if is_cur else "transparent"),
                text_color=("white" if is_cur else None),
                hover_color=("#1f6aa5" if is_cur else ("#e0e0e0", "#2b2b2b")),
                command=lambda c=cat: self._select_cat(c),
            )
            btn.pack(fill="x", padx=CAT_ITEM_PADX, pady=CAT_ITEM_PADY)

    def _on_close(self):
        self.destroy()

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
        wrap.grid(row=0, column=0, pady=EMPTY_TOP_PADY)
        ctk.CTkLabel(wrap, text="🐱", font=ctk.CTkFont(size=EMPTY_ICON_FONT_SIZE)).pack()
        ctk.CTkLabel(
            wrap, text="还没有猫咪资料\n点击左侧 “+ 添加猫咪” 开始",
            font=ctk.CTkFont(size=EMPTY_TEXT_FONT_SIZE), justify="center",
        ).pack(pady=EMPTY_TEXT_PADY)

    # ---------- 详情卡 ----------
    def _render_detail(self):
        self.main.update_idletasks()
        for w in self.main.winfo_children():
            w.destroy()
        self.event_scroller = None
        self.event_sections = None
        if not self.current:
            self._render_empty()
            return
        cat = self.current

        card = ctk.CTkFrame(self.main, corner_radius=DETAIL_CARD_CORNER)
        card.grid(row=0, column=0, padx=DETAIL_CARD_PAD, pady=DETAIL_CARD_PAD, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        photo_widget = self._build_photo(card, cat)
        photo_widget.grid(row=0, column=0, rowspan=2, padx=PHOTO_PAD, pady=PHOTO_PAD)

        name_row = ctk.CTkFrame(card, fg_color="transparent")
        name_row.grid(row=0, column=1, sticky="ew", padx=NAME_ROW_PADX, pady=NAME_ROW_PADY)
        ctk.CTkLabel(
            name_row, text=cat.name,
            font=ctk.CTkFont(size=NAME_FONT_SIZE, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(name_row, text="编辑", width=HEADER_BTN_WIDTH, height=HEADER_BTN_HEIGHT,
                      command=self._edit_cat).pack(side="left", padx=HEADER_BTN_PADX)
        ctk.CTkButton(name_row, text="体重管理", width=WEIGHT_BTN_WIDTH, height=HEADER_BTN_HEIGHT,
                  command=self._manage_weight).pack(side="left", padx=(0, HEADER_BTN_PADX))
        ctk.CTkButton(name_row, text="删除", width=HEADER_BTN_WIDTH, height=HEADER_BTN_HEIGHT,
                      fg_color="#c0392b", hover_color="#922b21",
                      command=self._delete_cat).pack(side="left")

        birth = cat.birth()
        days = age_days(birth)
        weeks, wd = age_weeks(birth)
        y, m, d = age_year_month(birth)
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=1, column=1, sticky="ew", padx=INFO_PADX, pady=INFO_PADY)
        self._age_chip(info, "出生日期", birth.strftime("%Y-%m-%d"))
        self._age_chip(info, "天数", f"{days} 天")
        self._age_chip(info, "周龄", f"{weeks} 周 {wd} 天")
        self._age_chip(info, "年月龄", f"{y} 岁 {m} 月 {d} 天")
        latest_w = cat.latest_weight()
        if latest_w:
            self._age_chip(info, "最新体重", f"{latest_w.weight_kg:.2f} kg")
        else:
            self._age_chip(info, "最新体重", "未记录")

        data_row = ctk.CTkFrame(card, fg_color="transparent")
        data_row.grid(row=2, column=1, sticky="ew", padx=DATA_ROW_PADX, pady=DATA_ROW_PADY)
        data_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            data_row,
            text=f"数据目录：{self._data_dir}",
            font=ctk.CTkFont(size=DATA_DIR_FONT),
            text_color=("gray40", "gray70"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            data_row,
            text="打开目录",
            width=OPEN_DIR_BTN_WIDTH,
            height=OPEN_DIR_BTN_HEIGHT,
            command=self._open_data_dir,
        ).grid(row=0, column=1, sticky="e", padx=OPEN_DIR_BTN_PADX)

        self.event_scroller = ctk.CTkScrollableFrame(self.main, corner_radius=RADIUS_NONE)
        self.event_scroller.grid(row=1, column=0, sticky="nsew")
        self.event_scroller.grid_columnconfigure(0, weight=1)
        # 降低滚动时重绘频率，缓解快速拖动滚动条时的拖影感。
        try:
            self.event_scroller._parent_canvas.configure(yscrollincrement=EVENT_SCROLL_Y_INCREMENT)
        except Exception:
            pass

        self.event_sections = ctk.CTkFrame(self.event_scroller, fg_color="transparent")
        self.event_sections.grid(row=0, column=0, sticky="ew")
        self.event_sections.grid_columnconfigure(0, weight=1)
        self._event_section_views = {}

        self._build_event_sections()

        self._refresh_event_sections()

    def _build_event_sections(self):
        if not self.event_sections:
            return
        specs = [
            ("future", 0, "🌱 未来计划"),
            ("past", 1, "📅 已完成事件"),
        ]
        for kind, row, title in specs:
            sec = ctk.CTkFrame(self.event_sections, corner_radius=SECTION_CORNER)
            sec.grid(row=row, column=0, padx=SECTION_PADX, pady=SECTION_PADY, sticky="ew")
            sec.grid_columnconfigure(0, weight=1)

            head = ctk.CTkFrame(sec, fg_color="transparent")
            head.grid(row=0, column=0, sticky="ew", padx=SECTION_HEAD_PADX, pady=SECTION_HEAD_PADY)
            head.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                head,
                text=title,
                font=ctk.CTkFont(size=SECTION_TITLE_FONT, weight="bold"),
            ).grid(row=0, column=0, sticky="w")
            count_label = ctk.CTkLabel(
                head,
                text="",
                font=ctk.CTkFont(size=SECTION_COUNT_FONT),
                text_color=("gray50", "gray60"),
            )
            count_label.grid(row=0, column=1, sticky="e", padx=SECTION_COUNT_PADX)
            count_label.grid_remove()
            ctk.CTkButton(
                head,
                text="+ 添加",
                width=SECTION_ADD_BTN_WIDTH,
                command=lambda k=kind: self._add_event(k),
            ).grid(row=0, column=2, sticky="e")

            empty = ctk.CTkFrame(sec, fg_color=("#fafafa", "#262626"),
                                 corner_radius=SECTION_EMPTY_CORNER)
            empty.grid(row=1, column=0, padx=SECTION_HEAD_PADX, pady=SECTION_PADY, sticky="ew")
            ctk.CTkLabel(
                empty,
                text="（暂无）",
                height=SECTION_EMPTY_HEIGHT,
                text_color=("gray50", "gray60"),
            ).pack(expand=True)

            body = ctk.CTkFrame(sec, fg_color="transparent")
            body.grid(row=1, column=0, sticky="ew", padx=SECTION_BODY_PADX, pady=SECTION_BODY_PADY)
            body.grid_columnconfigure(0, weight=1)
            body.grid_remove()

            self._event_section_views[kind] = {
                "section": sec,
                "count": count_label,
                "empty": empty,
                "body": body,
                "cards": {},
                "signatures": {},
            }

    def _refresh_event_sections(self):
        if not self.current or not self.event_sections:
            return
        cat = self.current
        self._update_event_section(
            "past",
            sorted([e for e in cat.events if e.kind == "past"],
                   key=lambda e: e.event_date),
        )
        self._update_event_section(
            "future",
            sorted([e for e in cat.events if e.kind == "future"],
                   key=lambda e: e.event_date),
        )

    def _event_signature(self, ev: Event) -> tuple[object, ...]:
        return (
            ev.title,
            ev.event_date,
            ev.kind,
            ev.note,
            ev.repeat_value,
            ev.repeat_unit,
        )

    def _update_event_section(self, kind: str, events: list[Event]):
        cat = self.current
        if cat is None:
            return
        view = self._event_section_views[kind]
        body = view["body"]
        empty = view["empty"]
        count_label = view["count"]
        cards = view["cards"]
        signatures = view["signatures"]

        count_label.configure(text=f"共 {len(events)} 条")
        if events:
            count_label.grid()
            empty.grid_remove()
            body.grid()
        else:
            count_label.grid_remove()
            body.grid_remove()
            empty.grid()

        event_ids = {ev.id for ev in events}
        for event_id in list(cards):
            if event_id not in event_ids:
                cards[event_id].destroy()
                del cards[event_id]
                signatures.pop(event_id, None)

        for index, ev in enumerate(events):
            signature = self._event_signature(ev)
            if ev.id not in cards or signatures.get(ev.id) != signature:
                if ev.id in cards:
                    cards[ev.id].destroy()
                cards[ev.id] = self._build_event_card(body, ev, cat)
                signatures[ev.id] = signature
            cards[ev.id].grid(row=index, column=0, sticky="ew", padx=EVENT_CARD_GRID_PADX, pady=EVENT_CARD_GRID_PADY)

    def _age_chip(self, parent, label, value):
        chip = ctk.CTkFrame(parent, corner_radius=CHIP_CORNER)
        chip.pack(side="left", padx=CHIP_OUTER_PADX, pady=CHIP_OUTER_PADY)
        ctk.CTkLabel(chip, text=label, font=ctk.CTkFont(size=CHIP_LABEL_FONT),
                 text_color=("gray40", "gray70")).pack(padx=CHIP_PADX, pady=CHIP_TOP_PADY)
        ctk.CTkLabel(chip, text=value,
                 font=ctk.CTkFont(size=CHIP_VALUE_FONT, weight="bold")).pack(padx=CHIP_PADX, pady=CHIP_BOTTOM_PADY)

    def _build_photo(self, parent, cat: Cat):
        size = CAT_PHOTO_SIZE
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
            font=ctk.CTkFont(size=CAT_PHOTO_FALLBACK_FONT),
            fg_color=("#f0f0f0", "#2b2b2b"), corner_radius=SECTION_EMPTY_CORNER,
        )

    def _build_event_card(self, parent, ev: Event, cat: Cat):
        # 颜色方案：已完成=蓝，未来待办=橙，未来过期=红
        d = ev.as_date()
        birth = cat.birth()
        days = (d - birth).days
        delta = (d - date.today()).days if ev.kind == "future" else 0
        if ev.kind == "past":
            accent = ("#3b82f6", "#60a5fa")
            badge_text, badge_fg = "已完成", ("#dbeafe", "#1e3a5f")
            badge_tc = ("#1e3a8a", "#bfdbfe")
        elif delta < 0:
            accent = ("#dc2626", "#ef4444")
            badge_text, badge_fg = "已过期", ("#fee2e2", "#5a1d1d")
            badge_tc = ("#991b1b", "#fca5a5")
        else:
            accent = ("#f59e0b", "#fbbf24")
            badge_text, badge_fg = "待办", ("#fef3c7", "#5a4416")
            badge_tc = ("#92400e", "#fde68a")

        card = ctk.CTkFrame(parent, corner_radius=EVENT_CARD_CORNER,
                            fg_color=("#ffffff", "#252525"),
                    border_width=EVENT_CARD_BORDER_WIDTH,
                            border_color=("#e5e7eb", "#333333"))
        card.configure(height=EVENT_CARD_FIXED_HEIGHT)
        card.grid_propagate(False)
        card.grid_columnconfigure(1, weight=1)
        card.grid_rowconfigure(4, weight=1)

        # 左侧状态色条
        strip = ctk.CTkFrame(card, width=EVENT_STRIP_WIDTH, corner_radius=EVENT_STRIP_CORNER, fg_color=accent)
        strip.grid(row=0, column=0, rowspan=6, sticky="ns", padx=EVENT_STRIP_PADX, pady=EVENT_STRIP_PADY)
        strip.grid_propagate(False)

        # 标题 + 状态徽章
        title_row = ctk.CTkFrame(card, fg_color="transparent")
        title_row.grid(row=0, column=1, sticky="ew", padx=EVENT_TITLE_PADX, pady=EVENT_TITLE_PADY)
        title_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_row, text=ev.title,
                     font=ctk.CTkFont(size=EVENT_TITLE_FONT, weight="bold"),
                     anchor="w"
                     ).grid(row=0, column=0, sticky="w")
        badge_row = ctk.CTkFrame(title_row, fg_color="transparent")
        badge_row.grid(row=0, column=1, sticky="e", padx=EVENT_STRIP_PADX)
        if ev.has_repeat():
            ctk.CTkLabel(
                badge_row,
                text="循环",
                font=ctk.CTkFont(size=EVENT_BADGE_FONT, weight="bold"),
                fg_color=("#dcfce7", "#16351f"),
                text_color=("#166534", "#86efac"),
                corner_radius=EVENT_BADGE_CORNER,
                padx=EVENT_BADGE_PADX,
                pady=EVENT_BADGE_PADY,
                height=EVENT_BADGE_HEIGHT,
            ).pack(side="left", padx=EVENT_BADGE_GAP)
        badge = ctk.CTkLabel(badge_row, text=badge_text,
                             font=ctk.CTkFont(size=EVENT_BADGE_FONT, weight="bold"),
                             fg_color=badge_fg, text_color=badge_tc,
                             corner_radius=EVENT_BADGE_CORNER, padx=EVENT_BADGE_PADX,
                             pady=EVENT_BADGE_PADY, height=EVENT_BADGE_HEIGHT)
        badge.pack(side="left")

        # 大日期
        date_str = d.strftime("%Y年%m月%d日")
        ctk.CTkLabel(card, text=f"📅  {date_str}",
                     font=ctk.CTkFont(size=EVENT_DATE_FONT),
                     text_color=("gray30", "gray80"),
                     anchor="w"
                     ).grid(row=1, column=1, sticky="w", padx=EVENT_DATE_PADX, pady=EVENT_DATE_PADY)

        # 信息微芯片
        sign = "-" if days < 0 else ""
        ad = abs(days)
        wks, wd = divmod(ad, 7)
        if days >= 0:
            y, m, dd = age_year_month(birth, d)
            ym_text = f"{y}岁{m}月{dd}天"
        else:
            y, m, dd = age_year_month(d, birth)
            ym_text = f"-{y}岁{m}月{dd}天"
        chips_row = ctk.CTkFrame(card, fg_color="transparent")
        chips_row.grid(row=2, column=1, sticky="w", padx=EVENT_CHIPS_PADX, pady=EVENT_CHIPS_PADY)
        self._mini_chip(chips_row, f"{sign}{ad}天")
        self._mini_chip(chips_row, f"{sign}{wks}周{wd}天")
        self._mini_chip(chips_row, ym_text)

        # 距今 / 已过 / 重复说明
        meta_parts = []
        if ev.kind == "future":
            meta_parts.append(f"距今 {delta} 天" if delta >= 0
                              else f"已过 {-delta} 天")
        if ev.has_repeat():
            meta_parts.append(
                f"🔁 每 {ev.repeat_value} "
                f"{REPEAT_LABEL_BY_UNIT.get(ev.repeat_unit, '')}")
        if meta_parts:
            ctk.CTkLabel(card, text="  ·  ".join(meta_parts),
                            font=ctk.CTkFont(size=EVENT_META_FONT),
                         text_color=("gray45", "gray65"), anchor="w"
                         ).grid(row=3, column=1, sticky="w",
                                padx=EVENT_META_PADX, pady=EVENT_META_PADY)

        # 备注块（固定高度，超出使用文本框滚动查看）
        note_box = ctk.CTkFrame(card, corner_radius=EVENT_NOTE_CORNER,
                                fg_color=("#f5f5f5", "#1e1e1e"))
        note_box.grid(row=4, column=1, sticky="nsew",
                  padx=EVENT_NOTE_PADX, pady=EVENT_NOTE_PADY)
        note_box.grid_columnconfigure(0, weight=1)
        note_box.grid_rowconfigure(0, weight=1)
        if ev.note:
            note_text = ctk.CTkTextbox(
                note_box,
                height=EVENT_NOTE_TEXT_HEIGHT,
                border_width=BORDER_NONE,
                fg_color="transparent",
                # 大量卡片同时显示滚动条会加重重绘，关闭自动滚动条可降低拖影。
                activate_scrollbars=False,
                wrap="word",
                font=ctk.CTkFont(size=EVENT_META_FONT),
            )
            note_text.grid(row=0, column=0, sticky="nsew", padx=EVENT_NOTE_TEXT_PAD, pady=EVENT_NOTE_TEXT_PAD)
            note_text.insert("1.0", ev.note)
            note_text.configure(state="disabled")
        else:
            ctk.CTkLabel(
                note_box,
                text="（无备注）",
                text_color=("gray50", "gray60"),
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=EVENT_NOTE_EMPTY_PAD, pady=EVENT_NOTE_EMPTY_PAD)

        # 底部操作区
        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=5, column=1, sticky="e", padx=EVENT_ACTION_PADX, pady=EVENT_ACTION_PADY)
        if ev.kind == "future":
            ctk.CTkButton(btns, text="完成", width=EVENT_ACTION_BTN_WIDTH, height=EVENT_ACTION_BTN_HEIGHT,
                          fg_color="#27ae60", hover_color="#1e8449",
                          command=lambda e=ev: self._complete_event(e)
                          ).pack(side="left", padx=EVENT_ACTION_BTN_GAP)
        ctk.CTkButton(btns, text="编辑", width=EVENT_ACTION_BTN_WIDTH, height=EVENT_ACTION_BTN_HEIGHT,
                      fg_color="transparent", border_width=BORDER_THIN,
                      text_color=("gray30", "gray80"),
                      command=lambda e=ev: self._edit_event(e)
                      ).pack(side="left", padx=EVENT_ACTION_BTN_GAP)
        ctk.CTkButton(btns, text="删除", width=EVENT_ACTION_BTN_WIDTH, height=EVENT_ACTION_BTN_HEIGHT,
                      fg_color="transparent", border_width=BORDER_THIN,
                      text_color=("#b91c1c", "#fca5a5"),
                      hover_color=("#fee2e2", "#3a1d1d"),
                      command=lambda e=ev: self._delete_event(e)
                      ).pack(side="left")
        return card

    def _mini_chip(self, parent, text: str):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(size=MINI_CHIP_FONT),
                     fg_color=("#f1f5f9", "#2f2f2f"),
                     text_color=("gray25", "gray80"),
                     corner_radius=MINI_CHIP_CORNER,
                     padx=MINI_CHIP_PADX,
                     pady=MINI_CHIP_PADY,
                     height=MINI_CHIP_HEIGHT
                     ).pack(side="left", padx=MINI_CHIP_GAP)

    def _open_data_dir(self):
        path = Path(self._data_dir)
        try:
            if os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录：{e}", parent=self)

    # ---------- 操作 ----------
    def _add_cat(self):
        CatDialog(self, on_save=self._on_cat_saved)

    def _edit_cat(self):
        if self.current:
            CatDialog(self, on_save=self._on_cat_saved, cat=self.current)

    def _manage_weight(self):
        if not self.current:
            return
        WeightDialog(self, cat=self.current, on_save=self._on_weight_saved)

    def _on_cat_saved(self, cat: Cat):
        if cat not in self.cats:
            self.cats.append(cat)
        save_cats(self.cats)
        self._select_cat(cat)

    def _on_weight_saved(self):
        save_cats(self.cats)
        self._render_detail()

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
        self._refresh_event_sections()

    def _on_event_saved(self, ev: Event):
        if not self.current:
            return
        if ev not in self.current.events:
            self.current.events.append(ev)
        save_cats(self.cats)
        self._refresh_event_sections()

    def _delete_event(self, ev: Event):
        if not self.current:
            return
        if not messagebox.askyesno("确认", f"删除事件「{ev.title}」？"):
            return
        self.current.events = [e for e in self.current.events if e.id != ev.id]
        save_cats(self.cats)
        self._refresh_event_sections()
