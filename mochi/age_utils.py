"""日期与年龄计算的纯函数。"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional


def age_days(birth: date, ref: Optional[date] = None) -> int:
    ref = ref or date.today()
    return (ref - birth).days


def age_weeks(birth: date, ref: Optional[date] = None) -> tuple[int, int]:
    d = age_days(birth, ref)
    return divmod(d, 7)  # (周, 余天)


def age_year_month(birth: date, ref: Optional[date] = None) -> tuple[int, int, int]:
    """返回 (年, 月, 日) —— 类似生日年龄计算。"""
    ref = ref or date.today()
    years = ref.year - birth.year
    months = ref.month - birth.month
    days = ref.day - birth.day
    if days < 0:
        # 借一个月
        months -= 1
        prev_month = (ref.replace(day=1) - timedelta(days=1))
        days += prev_month.day
    if months < 0:
        years -= 1
        months += 12
    return years, months, days


def date_from_weeks(birth: date, weeks: int, days: int = 0) -> date:
    return birth + timedelta(days=weeks * 7 + days)


def date_from_year_month(birth: date, years: int, months: int, days: int = 0) -> date:
    y = birth.year + years
    m = birth.month + months
    while m > 12:
        m -= 12
        y += 1
    while m < 1:
        m += 12
        y -= 1
    # 处理目标日不存在的情况（如 2/30）
    day = birth.day
    while True:
        try:
            d = date(y, m, day)
            break
        except ValueError:
            day -= 1
    return d + timedelta(days=days)


def add_offset(base: date, value: int, unit: str) -> date:
    """在 base 日期上加上 value*unit。"""
    if unit == "day":
        return base + timedelta(days=value)
    if unit == "week":
        return base + timedelta(weeks=value)
    if unit == "month":
        y = base.year + (base.month - 1 + value) // 12
        m = (base.month - 1 + value) % 12 + 1
        day = base.day
        while True:
            try:
                return date(y, m, day)
            except ValueError:
                day -= 1
    if unit == "year":
        try:
            return base.replace(year=base.year + value)
        except ValueError:
            # 2/29 -> 2/28
            return base.replace(year=base.year + value, day=28)
    return base
