"""提醒弹窗：纯视觉提示，全程静音（不加载/播放任何音频）"""
from __future__ import annotations

from PySide6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, QRectF, Property
from PySide6.QtGui import QColor, QPainter, QPainterPath, QFont
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QApplication
from PySide6.QtCore import Signal

from .theme import get, qss
from .widgets import water_drop_pixmap


class ReminderPopup(QWidget):
    drinkClicked = Signal()
    snoozeClicked = Signal()
    skipClicked = Signal()

    def __init__(self, theme="light", cup_ml=250, snooze_min=10, elapsed_text="", today_text=""):
        super().__init__()
        self.cup_ml = cup_ml
        self.snooze_min = snooze_min
        self.theme = theme
        c = get(theme)

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.setFixedSize(360, 198)

        card = QWidget(self)
        card.setObjectName("card")
        card.setGeometry(10, 10, 340, 178)

        # 图标
        icon = QLabel(card)
        pm = water_drop_pixmap(44, c["primary"], dark=(theme == "dark"))
        icon.setPixmap(pm)
        icon.setFixedSize(44, 44)
        icon.setStyleSheet("background: transparent;")

        title = QLabel("该喝水啦", card)
        title.setObjectName("title")
        title.setFont(QFont("Microsoft YaHei UI", 14, QFont.Bold))

        sub = QLabel(elapsed_text or "休息一下，补充一杯水", card)
        sub.setObjectName("sub")
        sub.setWordWrap(False)
        sub.setFixedWidth(240)

        head_text = QVBoxLayout()
        head_text.setSpacing(2)
        head_text.addWidget(title)
        head_text.addWidget(sub)

        head = QHBoxLayout()
        head.setSpacing(12)
        head.setContentsMargins(0, 0, 0, 0)
        head.addWidget(icon)
        head.addLayout(head_text)
        head.addStretch(1)

        self.btn_drink = QPushButton(f"喝了 +{cup_ml}ml", card)
        self.btn_drink.setObjectName("primary")
        self.btn_drink.setCursor(Qt.PointingHandCursor)
        self.btn_drink.clicked.connect(self.drinkClicked.emit)

        self.btn_snooze = QPushButton(f"稍后 {snooze_min} 分钟", card)
        self.btn_snooze.setObjectName("ghost")
        self.btn_snooze.setCursor(Qt.PointingHandCursor)
        self.btn_snooze.clicked.connect(self.snoozeClicked.emit)

        btns = QHBoxLayout()
        btns.setSpacing(8)
        btns.addWidget(self.btn_drink, 3)
        btns.addWidget(self.btn_snooze, 2)

        close = QPushButton("×", card)
        close.setObjectName("titlebtn")
        close.setFixedSize(22, 22)
        close.setCursor(Qt.PointingHandCursor)
        close.clicked.connect(self.skipClicked.emit)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.addStretch(1)
        top.addWidget(close)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 8, 16, 14)
        layout.setSpacing(10)
        layout.addLayout(top)
        layout.addLayout(head)
        layout.addWidget(QLabel(today_text, card, objectName="sub"))
        layout.addLayout(btns)

        self.setStyleSheet(qss(theme))

    def paintEvent(self, event):
        c = get(self.theme)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        # 外阴影（柔和）
        p.setBrush(QColor(0, 0, 0, 22))
        p.drawRoundedRect(QRectF(13, 14, 334, 178), 16, 16)
        p.setBrush(QColor(c["card"]))
        p.drawRoundedRect(QRectF(10, 10, 340, 178), 16, 16)
        # 左侧高亮条
        p.setBrush(QColor(c["primary"]))
        p.drawRoundedRect(QRectF(10, 10, 4, 178), 2, 2)

    def show_at_top(self):
        """从屏幕顶部滑入（居中），静默无提示音"""
        screen = QApplication.primaryScreen()
        geo = screen.availableGeometry()
        x = geo.left() + (geo.width() - self.width()) // 2
        y = geo.top() + 18
        self.move(x, y - self.height() - 10)
        self.setWindowOpacity(0.0)
        self.show()

        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(260)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

        self._pos_anim = QPropertyAnimation(self, b"pos")
        self._pos_anim.setDuration(320)
        self._pos_anim.setStartValue(QPoint(x, y - self.height() - 10))
        self._pos_anim.setEndValue(QPoint(x, y))
        self._pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._pos_anim.start()
