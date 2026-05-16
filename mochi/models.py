"""数据模型与持久化。"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path


def app_dir() -> Path:
    """返回数据目录（兼容 PyInstaller 打包后场景）。

    - 打包后：exe 同目录 / data
    - 开发模式：项目根目录 / data（即 mochi 包的上一级）
    """
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).resolve().parent.parent
    d = base / "data"
    d.mkdir(parents=True, exist_ok=True)
    (d / "photos").mkdir(parents=True, exist_ok=True)
    return d


DATA_FILE = app_dir() / "cats.json"
PHOTO_DIR = app_dir() / "photos"


@dataclass
class Event:
    id: str
    title: str
    event_date: str          # ISO YYYY-MM-DD
    kind: str                # 'past' | 'future'
    note: str = ""
    repeat_value: int = 0    # 0 表示不重复
    repeat_unit: str = ""    # 'day' | 'week' | 'month' | 'year'

    def as_date(self) -> date:
        return date.fromisoformat(self.event_date)

    def has_repeat(self) -> bool:
        return self.repeat_value > 0 and self.repeat_unit in {"day", "week", "month", "year"}


@dataclass
class Cat:
    id: str
    name: str
    birth_date: str          # ISO
    photo: str = ""          # 相对 photos/ 文件名
    events: list[Event] = field(default_factory=list)

    def birth(self) -> date:
        return date.fromisoformat(self.birth_date)


def load_cats() -> list[Cat]:
    if not DATA_FILE.exists():
        return []
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    cats: list[Cat] = []
    for c in raw:
        events = []
        for e in c.get("events", []):
            events.append(Event(
                id=e["id"], title=e["title"],
                event_date=e["event_date"], kind=e["kind"],
                note=e.get("note", ""),
                repeat_value=int(e.get("repeat_value", 0) or 0),
                repeat_unit=e.get("repeat_unit", "") or "",
            ))
        cats.append(Cat(
            id=c["id"], name=c["name"], birth_date=c["birth_date"],
            photo=c.get("photo", ""), events=events,
        ))
    return cats


def save_cats(cats: list[Cat]) -> None:
    data = [asdict(c) for c in cats]
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
