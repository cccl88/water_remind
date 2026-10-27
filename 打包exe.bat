@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo 未找到虚拟环境，请先运行「安装依赖.bat」
    pause
    exit /b 1
)

echo [1/2] 生成图标 app.ico ...
".venv\Scripts\python.exe" _make_icon.py
if errorlevel 1 (
    echo 图标生成失败
    pause
    exit /b 1
)

echo [2/2] 正在打包 exe（约 1-3 分钟，请耐心等待）...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --noconsole ^
    --name WaterReminder ^
    --icon app.ico ^
    --hidden-import PySide6.QtNetwork ^
    main.py

if errorlevel 1 (
    echo 打包失败
    pause
    exit /b 1
)

echo.
echo 打包完成：dist\WaterReminder.exe
echo.
pause
