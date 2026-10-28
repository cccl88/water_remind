"""桌宠气泡：显示台词 + 喝水/稍后按钮"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QFont
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Signal

from ui.theme import get, qss


class PetBubble(QWidget):
    drinkClicked = Signal()
    snoozeClicked = Signal()
    skipClicked = Signal()

    def __init__(self, text: str, theme: str = "light", with_actions: bool = True):
        super().__init__()
        self.c = get(theme)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        self.text = QLabel(text)
        self.text.setWordWrap(True)
        self.text.setObjectName("pet_bubble_text")
        self.text.setStyleSheet(
            f"QLabel#pet_bubble_text {{ color: {self.c['text']}; font-family: 'Microsoft YaHei UI'; "
            f"font-size: 12px; background: transparent; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 16)
        layout.setSpacing(10)
        layout.addWidget(self.text)

        if with_actions:
            row = QHBoxLayout()
            row.setSpacing(8)
            btn_d = QPushButton("喝啦")
            btn_d.setObjectName("pet_btn")
            btn_d.setStyleSheet(self._btn_qss(primary=True))
            btn_d.setCursor(Qt.PointingHandCursor)
            btn_d.clicked.connect(self.drinkClicked.emit)
            btn_s = QPushButton("稍后")
            btn_s.setObjectName("pet_btn")
            btn_s.setStyleSheet(self._btn_qss(primary=False))
            btn_s.setCursor(Qt.PointingHandCursor)
            btn_s.clicked.connect(self.snoozeClicked.emit)
            btn_x = QPushButton("跳过")
            btn_x.setObjectName("pet_btn")
            btn_x.setStyleSheet(self._btn_qss(primary=False))
            btn_x.setCursor(Qt.PointingHandCursor)
            btn_x.clicked.connect(self.skipClicked.emit)
            row.addWidget(btn_d)
            row.addWidget(btn_s)
            row.addWidget(btn_x)
            layout.addLayout(row)
        else:
            # 纯提示气泡：点击关闭
            self.setCursor(Qt.PointingHandCursor)

        self.setFixedWidth(230)
        self.adjustSize()
        # 底部留出小三角高度
        self.resize(self.width(), self.sizeHint().height() + 12)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.close)

    def _btn_qss(self, primary: bool) -> str:
        c = self.c
        if primary:
            return (
                "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                f" stop:0 {c['primary']}, stop:1 {c['primary2']}); color: white; border: none;"
                " border-radius: 10px; padding: 4px 10px; font-size: 12px; font-weight: 700; }"
                "QPushButton:hover { opacity: 0.92; }"
            )
        return (
            f"QPushButton {{ background: transparent; color: {c['sub']}; border: 1px solid {c['border']};"
            " border-radius: 10px; padding: 4px 10px; font-size: 12px; }"
            f"QPushButton:hover {{ background: {c['primary_soft']}; color: {c['primary']}; }}"
        )

    def start_auto_close(self, ms: int = 12000):
        self._timer.start(ms)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        rect_h = h - 12
        # 阴影
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 20))
        p.drawRoundedRect(QRectF(3, 4, w - 6, rect_h - 4), 14, 14)
        # 气泡主体
        p.setBrush(QColor(self.c["card"]))
        p.drawRoundedRect(QRectF(2, 2, w - 6, rect_h - 4), 14, 14)
        # 底部小三角（指向桌宠）
        tri = QPainterPath()
        tx = w * 0.5
        tri.moveTo(tx - 8, rect_h - 3)
        tri.lineTo(tx + 8, rect_h - 3)
        tri.lineTo(tx, h - 2)
        tri.closeSubpath()
        p.setBrush(QColor(self.c["card"]))
        p.drawPath(tri)
