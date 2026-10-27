"""自绘控件：饮水进度环、近 7 天柱状图、水滴图标"""
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, QPointF, Property, QTimer, QRect, Signal
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QBrush,
    QLinearGradient,
    QFont,
    QPixmap,
    QPainterPath,
    QFontMetrics,
)
from PySide6.QtWidgets import QWidget, QSizePolicy

from .theme import get


class RingProgress(QWidget):
    """圆环进度：显示 已喝 / 目标"""

    def __init__(self, parent=None, theme="light"):
        super().__init__(parent)
        self.theme = theme
        self._value = 0.0  # 0.0 ~ 1.0
        self._display = 0.0  # 动画插值
        self.current_ml = 0
        self.goal_ml = 2000
        self.setMinimumSize(190, 190)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._step)

    def setValue(self, v: float, animate=True):
        v = max(0.0, min(1.0, v))
        if animate:
            self._value = v
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._value = v
            self._display = v
            self.update()

    def _step(self):
        diff = self._value - self._display
        if abs(diff) < 0.002:
            self._display = self._value
            self._timer.stop()
        else:
            self._display += diff * 0.18
        self.update()

    def paintEvent(self, event):
        c = get(self.theme)
        side = min(self.width(), self.height())
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen_w = max(10, int(side * 0.075))
        rect = QRectF(pen_w / 2 + 2, pen_w / 2 + 2, side - pen_w - 4, side - pen_w - 4)

        # 底环
        pen = QPen(QColor(c["track"]), pen_w)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, 90 * 16, -360 * 16)

        # 进度环
        if self._display > 0.001:
            grad = QLinearGradient(0, 0, side, side)
            grad.setColorAt(0, QColor(c["primary"]))
            grad.setColorAt(1, QColor(c["primary2"]))
            pen = QPen(QBrush(grad), pen_w)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawArc(rect, 90 * 16, int(-360 * 16 * self._display))

        # 中心文字
        pct = int(round(self._display * 100))
        f1 = QFont("Microsoft YaHei UI", int(side * 0.155), QFont.Bold)
        p.setFont(f1)
        p.setPen(QColor(c["text"]))
        p.drawText(QRectF(0, side * 0.30, side, side * 0.22), Qt.AlignCenter, f"{self.current_ml}")

        f2 = QFont("Microsoft YaHei UI", int(side * 0.058))
        p.setFont(f2)
        p.setPen(QColor(c["sub"]))
        p.drawText(QRectF(0, side * 0.50, side, side * 0.12), Qt.AlignCenter, f"/ {self.goal_ml} ml")

        f3 = QFont("Microsoft YaHei UI", int(side * 0.062), QFont.DemiBold)
        p.setFont(f3)
        p.setPen(QColor(c["primary"]))
        p.drawText(QRectF(0, side * 0.635, side, side * 0.12), Qt.AlignCenter, f"{pct}%")


class BarChart(QWidget):
    """最近 7 天饮水量柱状图"""

    def __init__(self, parent=None, theme="light"):
        super().__init__(parent)
        self.theme = theme
        self.data = []  # [(date, ml)]
        self.goal = 2000
        self.setFixedHeight(96)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def setData(self, data, goal):
        self.data = data
        self.goal = goal
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return
        c = get(self.theme)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        pad = 6
        chart_h = h - 24
        max_v = max([v for _, v in self.data] + [self.goal]) * 1.15 or 1

        # 目标虚线
        y_goal = pad + chart_h - chart_h * (self.goal / max_v)
        pen = QPen(QColor(c["warn"]))
        pen.setStyle(Qt.DashLine)
        pen.setWidth(1)
        p.setPen(pen)
        p.drawLine(QPointF(2, y_goal), QPointF(w - 2, y_goal))

        n = len(self.data)
        slot = w / n
        bar_w = min(26.0, slot * 0.46)
        for i, (d, v) in enumerate(self.data):
            cx = slot * i + slot / 2
            bh = max(3.0, chart_h * (v / max_v))
            top = pad + chart_h - bh
            rect = QRectF(cx - bar_w / 2, top, bar_w, bh)
            path = QPainterPath()
            path.addRoundedRect(rect, bar_w / 2, bar_w / 2)
            grad = QLinearGradient(0, top, 0, top + bh)
            if v >= self.goal:
                grad.setColorAt(0, QColor(c["success"]))
                grad.setColorAt(1, QColor(c["success"]).lighter(120))
            else:
                grad.setColorAt(0, QColor(c["primary"]))
                grad.setColorAt(1, QColor(c["primary2"]))
            p.fillPath(path, QBrush(grad))

            # 日期标签
            f = QFont("Microsoft YaHei UI", 8)
            p.setFont(f)
            is_today = i == n - 1
            p.setPen(QColor(c["text"] if is_today else c["sub"]))
            label = "今天" if is_today else f"{d.month}/{d.day}"
            p.drawText(QRectF(cx - slot / 2, h - 19, slot, 14), Qt.AlignCenter, label)


def water_drop_pixmap(size: int = 64, color: str = "#2E90FF", dark: bool = False) -> QPixmap:
    """绘制水滴图标"""
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    s = size

    # 圆形底
    bg = QColor("#FFFFFF" if not dark else "#16202C")
    p.setBrush(QBrush(bg))
    p.setPen(Qt.NoPen)
    p.drawEllipse(1, 1, s - 2, s - 2)

    grad = QLinearGradient(s * 0.3, s * 0.2, s * 0.7, s * 0.9)
    grad.setColorAt(0, QColor(color).lighter(115))
    grad.setColorAt(1, QColor(color))
    p.setBrush(QBrush(grad))

    path = QPainterPath()
    path.moveTo(s * 0.5, s * 0.16)
    path.cubicTo(s * 0.78, s * 0.46, s * 0.76, s * 0.78, s * 0.5, s * 0.84)
    path.cubicTo(s * 0.24, s * 0.78, s * 0.22, s * 0.46, s * 0.5, s * 0.16)
    path.closeSubpath()
    p.drawPath(path)

    # 高光
    p.setBrush(QBrush(QColor(255, 255, 255, 150)))
    p.drawEllipse(QPointF(s * 0.38, s * 0.60), s * 0.09, s * 0.13)
    p.end()
    return pm


class Switch(QWidget):
    """轻量开关控件"""

    toggled = Signal(bool)

    def __init__(self, parent=None, theme="light", checked=True):
        super().__init__(parent)
        self.theme = theme
        self._checked = checked
        self.setFixedSize(44, 24)
        self.setCursor(Qt.PointingHandCursor)

    def isChecked(self):
        return self._checked

    def setChecked(self, v: bool):
        if self._checked != v:
            self._checked = v
            self.update()
            self.toggled.emit(v)

    def mousePressEvent(self, e):
        self.setChecked(not self._checked)
        super().mousePressEvent(e)

    def paintEvent(self, e):
        c = get(self.theme)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        on = self._checked
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(c["primary"] if on else c["track"])))
        p.drawRoundedRect(QRectF(0, 0, self.width(), self.height()), 12, 12)
        d = self.height() - 6
        x = self.width() - d - 3 if on else 3
        p.setBrush(QBrush(QColor("#FFFFFF")))
        p.drawEllipse(QPointF(x + d / 2, self.height() / 2), d / 2, d / 2)
