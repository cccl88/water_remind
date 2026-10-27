@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
    echo 尚未安装依赖，正在为你安装（约需 1-3 分钟）...
    call "安装依赖.bat"
)

start "" ".venv\Scripts\pythonw.exe" "%~dp0main.py"
exit /b 0
