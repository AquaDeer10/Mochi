# Mochi · 小猫成长管理

一个现代化风格的 Python 桌面 GUI，用于记录猫咪的基础信息、成长年龄、历史事件与未来计划。

## 功能
- 维护猫咪信息：名称、出生日期、照片
- 资料卡同时显示：天数、周龄、年月龄
- 添加 **历史事件 / 未来计划**，支持三种录入方式：
  - 按日期
  - 按周龄（X 周 X 天）
  - 按年月龄（X 年 X 月 X 天）
- 事件按时间排序，自动显示 “距今 N 天” 等信息
- 数据保存在程序目录下的 `data/cats.json`，照片复制到 `data/photos/`

## 运行
```powershell
pip install -r requirements.txt
python app.py
```

## 打包为独立 exe
```powershell
pip install -r requirements.txt
pip install pyinstaller
.\build.bat
```
完成后产物位于 `dist\Mochi.exe`，可直接复制运行。
