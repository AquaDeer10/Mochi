"""通用 UI 控件与常量。"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

import customtkinter as ctk

from .layout_constants import (
    DATE_PICKER_DAY_WIDTH,
    DATE_PICKER_ITEM_PADX,
    DATE_PICKER_MONTH_WIDTH,
    DATE_PICKER_YEAR_WIDTH,
)


REPEAT_UNIT_LABELS = [("天", "day"), ("周", "week"), ("月", "month"), ("年", "year")]
REPEAT_LABEL_BY_UNIT = {u: lab for lab, u in REPEAT_UNIT_LABELS}


class DatePicker(ctk.CTkFrame):
    """三个下拉框组成的简易日期选择器（年/月/日）。"""

    def __init__(self, master, initial: Optional[date] = None, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        initial = initial or date.today()
        years = [str(y) for y in range(1990, date.today().year + 2)]
        self.var_y = ctk.StringVar(value=str(initial.year))
        self.var_m = ctk.StringVar(value=f"{initial.month:02d}")
        self.var_d = ctk.StringVar(value=f"{initial.day:02d}")

        self.cb_y = ctk.CTkComboBox(self, values=years, width=DATE_PICKER_YEAR_WIDTH, variable=self.var_y,
                                    command=lambda _=None: self._refresh_days())
        self.cb_m = ctk.CTkComboBox(self, values=[f"{i:02d}" for i in range(1, 13)],
                        width=DATE_PICKER_MONTH_WIDTH, variable=self.var_m,
                                    command=lambda _=None: self._refresh_days())
        self.cb_d = ctk.CTkComboBox(self, values=[f"{i:02d}" for i in range(1, 32)],
                        width=DATE_PICKER_DAY_WIDTH, variable=self.var_d)
        self.cb_y.pack(side="left", padx=DATE_PICKER_ITEM_PADX)
        ctk.CTkLabel(self, text="年").pack(side="left")
        self.cb_m.pack(side="left", padx=DATE_PICKER_ITEM_PADX)
        ctk.CTkLabel(self, text="月").pack(side="left")
        self.cb_d.pack(side="left", padx=DATE_PICKER_ITEM_PADX)
        ctk.CTkLabel(self, text="日").pack(side="left")
        self._refresh_days()

    def _refresh_days(self):
        try:
            y = int(self.var_y.get()); m = int(self.var_m.get())
        except ValueError:
            return
        if m == 12:
            last = date(y + 1, 1, 1) - timedelta(days=1)
        else:
            last = date(y, m + 1, 1) - timedelta(days=1)
        self.cb_d.configure(values=[f"{i:02d}" for i in range(1, last.day + 1)])
        if int(self.var_d.get() or 1) > last.day:
            self.var_d.set(f"{last.day:02d}")

    def get_date(self) -> date:
        return date(int(self.var_y.get()), int(self.var_m.get()), int(self.var_d.get()))

    def set_date(self, d: date):
        self.var_y.set(str(d.year))
        self.var_m.set(f"{d.month:02d}")
        self._refresh_days()
        self.var_d.set(f"{d.day:02d}")
