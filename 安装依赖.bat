@echo off
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set PY=py -3
) else (
    set PY=python
)

echo 正在创建虚拟环境 .venv ...
%PY% -m venv .venv
if errorlevel 1 (
    echo 创建虚拟环境失败，请确认已安装 Python 3.9 及以上版本。
    pause
    exit /b 1
)

echo 正在安装 PySide6（使用腾讯云镜像）...
".venv\Scripts\python.exe" -m pip install -i https://mirrors.cloud.tencent.com/pypi/simple PySide6-Essentials
if errorlevel 1 (
    echo 镜像安装失败，改用官方源重试...
    ".venv\Scripts\python.exe" -m pip install PySide6-Essentials
    if errorlevel 1 (
        echo 安装失败，可尝试手动执行：
        echo   .venv\Scripts\python.exe -m pip install PySide6-Essentials
        pause
        exit /b 1
    )
)

echo 依赖安装完成，双击「启动喝水提醒.bat」即可运行。
pause
