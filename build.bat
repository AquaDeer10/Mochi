@echo off
REM 一键打包脚本：生成单文件 exe（dist\Mochi.exe）
REM 首次使用前请先安装依赖：
REM    .venv\Scripts\activate
REM    pip install -r requirements.txt
REM    pip install pyinstaller

setlocal
cd /d "%~dp0"

REM 优先使用项目内 .venv 的 Python，避免系统 Python 缺失 stdlib（如 _ctypes）
if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else (
    echo [!] 未找到 .venv，将使用系统 python
    set "PY=python"
)

echo [*] Using interpreter: %PY%

"%PY%" -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo [!] 在该解释器内安装 pyinstaller...
    "%PY%" -m pip install pyinstaller || goto :err
)

REM 用 --collect-all 调用官方 hook，自动收集 customtkinter 的代码、资源、依赖
"%PY%" -m PyInstaller --noconfirm --clean ^
    --name Mochi ^
    --windowed ^
    --onefile ^
    --collect-all customtkinter ^
    app.py
if errorlevel 1 goto :err

echo.
echo [OK] 打包完成：dist\Mochi.exe
exit /b 0

:err
echo [X] 打包失败
exit /b 1
