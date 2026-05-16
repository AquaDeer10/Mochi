"""包入口：python -m mochi.app 或通过根目录 app.py 启动。"""
from __future__ import annotations

from .ui.main_window import App


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()
