"""配色与样式表"""
from __future__ import annotations

PALETTE = {
    "light": {
        "bg": "#EAF1F8",
        "card": "#FFFFFF",
        "panel": "#F4F8FC",
        "text": "#172433",
        "sub": "#6C8099",
        "border": "#E2EBF4",
        "primary": "#2E90FF",
        "primary2": "#4FC3F7",
        "primary_soft": "#E8F3FF",
        "success": "#22C58B",
        "warn": "#FFB020",
        "track": "#E7EFF7",
        "shadow": "#B9CBDD",
        "hover": "#F0F6FC",
    },
    "dark": {
        "bg": "#0E1620",
        "card": "#16202C",
        "panel": "#1B2735",
        "text": "#E7EFF7",
        "sub": "#8DA2B8",
        "border": "#253444",
        "primary": "#3D9BFF",
        "primary2": "#5FD0FF",
        "primary_soft": "#1E3247",
        "success": "#2ED3A0",
        "warn": "#FFB020",
        "track": "#22303E",
        "shadow": "#050A10",
        "hover": "#1D2A38",
    },
}


def get(name: str) -> dict:
    return PALETTE.get(name, PALETTE["light"])


def qss(theme: str = "light") -> str:
    c = get(theme)
    return f"""
    * {{ font-family: "Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI"; }}
    QWidget#root {{
        background: {c['card']};
        border-radius: 16px;
    }}
    QWidget {{
        color: {c['text']};
        background: transparent;
    }}
    QLabel {{ background: transparent; }}
    QLabel#title {{ font-size: 15px; font-weight: 600; color: {c['text']}; }}
    QLabel#appname {{ font-size: 13px; font-weight: 600; color: {c['text']}; }}
    QLabel#sub {{ font-size: 12px; color: {c['sub']}; }}
    QLabel#section {{ font-size: 12px; font-weight: 600; color: {c['sub']}; letter-spacing: 1px; }}
    QLabel#value {{ font-size: 13px; font-weight: 600; color: {c['primary']}; }}
    QWidget#card {{
        background: {c['panel']};
        border-radius: 12px;
    }}
    QWidget#divider {{ background: {c['border']}; }}
    QPushButton {{
        border: none;
        border-radius: 8px;
        padding: 7px 14px;
        font-size: 12px;
        background: {c['primary_soft']};
        color: {c['text']};
    }}
    QPushButton:hover {{ background: {c['border']}; }}
    QPushButton#primary {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {c['primary']}, stop:1 {c['primary2']});
        color: #FFFFFF;
        font-weight: 600;
        padding: 10px 16px;
        font-size: 13px;
        border-radius: 10px;
    }}
    QPushButton#primary:hover {{ background: {c['primary']}; }}
    QPushButton#ghost {{
        background: transparent;
        border: 1px solid {c['border']};
        color: {c['sub']};
    }}
    QPushButton#ghost:hover {{ background: {c['hover']}; color: {c['text']}; }}
    QPushButton#titlebtn {{
        background: transparent;
        border-radius: 6px;
        color: {c['sub']};
        font-size: 14px;
        padding: 2px 8px;
    }}
    QPushButton#titlebtn:hover {{ background: {c['hover']}; color: {c['text']}; }}
    QPushButton#closebtn:hover {{ background: #FF5A5F; color: #FFFFFF; }}
    QSlider::groove:horizontal {{
        height: 5px; background: {c['track']}; border-radius: 3px;
    }}
    QSlider::sub-page:horizontal {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {c['primary']}, stop:1 {c['primary2']});
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        width: 15px; margin: -6px 0; border-radius: 8px;
        background: #FFFFFF; border: 3px solid {c['primary']};
    }}
    QTimeEdit {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 5px 8px;
        font-size: 12px;
        color: {c['text']};
    }}
    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 4px; min-height: 30px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QSystemTrayIcon {{ }}
    """
