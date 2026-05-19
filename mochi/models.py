"""数据模型与持久化。"""
from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path


def _legacy_app_dir() -> Path:
    """返回旧版数据目录位置。"""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "data"


def _migrate_legacy_data(target: Path) -> None:
    """首次切换到固定目录时，将旧版同级 data 迁移到新目录。"""
    legacy = _legacy_app_dir()
    legacy_file = legacy / "cats.json"
    target_file = target / "cats.json"
    legacy_photos = legacy / "photos"
    target_photos = target / "photos"

    if target_file.exists() or not legacy_file.exists():
        return

    shutil.copy2(legacy_file, target_file)
    if legacy_photos.exists():
        target_photos.mkdir(parents=True, exist_ok=True)
        for photo in legacy_photos.iterdir():
            if photo.is_file():
                shutil.copy2(photo, target_photos / photo.name)


def app_dir() -> Path:
    """返回固定的数据目录。

    Windows 默认使用 %LOCALAPPDATA%\\Mochi，
    避免 exe 移动位置后数据跟着漂移或遇到写权限问题。
    首次运行会自动从旧版同级 data 目录迁移现有数据。
    """
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        d = Path(local_app_data) / "Mochi"
    else:
        d = Path.home() / "AppData" / "Local" / "Mochi"
    d.mkdir(parents=True, exist_ok=True)
    (d / "photos").mkdir(parents=True, exist_ok=True)
    _migrate_legacy_data(d)
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
class WeightRecord:
    record_date: str  # ISO YYYY-MM-DD
    weight_kg: float

    def as_date(self) -> date:
        return date.fromisoformat(self.record_date)


@dataclass
class Cat:
    id: str
    name: str
    birth_date: str          # ISO
    photo: str = ""          # 相对 photos/ 文件名
    events: list[Event] = field(default_factory=list)
    weights: list[WeightRecord] = field(default_factory=list)

    def birth(self) -> date:
        return date.fromisoformat(self.birth_date)

    def latest_weight(self) -> WeightRecord | None:
        if not self.weights:
            return None
        return max(self.weights, key=lambda w: w.record_date)


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
        weights = []
        for w in c.get("weights", []):
            try:
                weights.append(WeightRecord(
                    record_date=w["record_date"],
                    weight_kg=float(w["weight_kg"]),
                ))
            except Exception:
                continue
        cats.append(Cat(
            id=c["id"], name=c["name"], birth_date=c["birth_date"],
            photo=c.get("photo", ""), events=events, weights=weights,
        ))
    return cats


def save_cats(cats: list[Cat]) -> None:
    data = [asdict(c) for c in cats]
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
