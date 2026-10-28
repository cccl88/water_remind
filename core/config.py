"""应用配置：读写 JSON，持久化到 %APPDATA%\\WaterReminder"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict, field

APP_NAME = "WaterReminder"


def app_data_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


CONFIG_PATH = os.path.join(app_data_dir(), "config.json")
DATA_PATH = os.path.join(app_data_dir(), "history.json")

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


@dataclass
class Config:
    # 提醒间隔（分钟）——用户可调，核心需求
    interval_min: int = 45
    # 单杯水量（毫升）
    cup_ml: int = 250
    # 每日目标（毫升）
    goal_ml: int = 2000
    # 提醒总开关
    enabled: bool = True
    # 只在此时段内提醒（24 小时制 "HH:MM"）
    active_from: str = "08:00"
    active_to: str = "22:00"
    # 稍后提醒的顺延分钟
    snooze_min: int = 10
    # 静默模式：绝不播放任何提示音（本应用不内置任何音频资源）
    silent: bool = True
    # 开机自启
    auto_start: bool = False
    # 主题：light / dark
    theme: str = "light"
    # 桌宠
    pet_enabled: bool = True
    personality: str = "tsundere"  # tsundere / gentle / coquettish
    pet_name: str = "凛"
    pet_pos: list = field(default_factory=list)
    # 提醒时是否同时弹卡片（默认只用桌宠气泡）
    show_card: bool = False
    # 每次提醒顺延但未饮水时，是否自动累计记录（False 表示只在手动确认后记录）
    window_geometry: list = field(default_factory=list)

    # ---------- 序列化 ----------
    @classmethod
    def load(cls) -> "Config":
        cfg = cls()
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, v in data.items():
                    if hasattr(cfg, k):
                        setattr(cfg, k, v)
            except Exception:
                pass
        return cfg

    def save(self) -> None:
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=2)
        except Exception:
            pass


def _launch_command() -> str:
    """生成用于开机自启的命令行"""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
    exe_dir = os.path.dirname(sys.executable)
    pythonw = os.path.join(exe_dir, "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable
    return f'"{pythonw}" "{main_py}"'


def set_auto_start(enabled: bool) -> bool:
    """写入 / 删除 HKCU Run 自启项"""
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _launch_command())
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception:
        return False


def is_auto_start() -> bool:
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(value)
    except Exception:
        return False
