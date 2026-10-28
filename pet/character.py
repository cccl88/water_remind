"""原创 Q 版桌宠角色绘制：白发少女「凛」

设计说明（避免侵权）：
- 角色为原创，仅采用「白发 + 红色发饰 + 傲娇性格」等通用二次元元素
- 不使用任何动漫作品的角色名、制服、配色组合或标志性设定
- 服装为原创白色连衣裙 + 红色蝴蝶结，非任何作品战斗服
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QBrush, QPen, QLinearGradient

# ---------- 配色 ----------
HAIR_MAIN = QColor("#F7F9FF")
HAIR_SHADE = QColor("#D8E0F2")
HAIR_LINE = QColor("#AEB9D4")
SKIN = QColor("#FFE6D8")
SKIN_SHADE = QColor("#F4C6AE")
EYE = QColor("#3F4C6E")
EYE_TOP = QColor("#66769E")
BLUSH = QColor(255, 130, 152)
CLOTH = QColor("#FFFFFF")
CLOTH_SHADE = QColor("#E4EAF6")
ACCENT = QColor("#E8536B")
ACCENT_DARK = QColor("#C2394F")
LINE = QColor("#8A93A8")
SOCK = QColor("#F2F5FC")


def _ellipse(p, x, y, rx, ry):
    p.drawEllipse(QRectF(x - rx, y - ry, rx * 2, ry * 2))


class Character:
    """Q 版角色绘制器（2 头身 + 落地裙）"""

    def paint(self, p: QPainter, w: int, h: int, expr: str = "idle", t: float = 0.0,
              blink: bool = False, theme: str = "light"):
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)

        cx = w * 0.5
        head_cy = h * 0.335
        rx = w * 0.335
        ry = h * 0.26

        # 呼吸浮动（由外部偏移控制，这里仅轻微缩放身体）
        self._shadow(p, cx, w, h)
        self._hair_back(p, cx, head_cy, rx, ry)
        self._body(p, cx, head_cy + ry * 0.86, w, h, t)
        self._head(p, cx, head_cy, rx, ry)
        self._hair_front(p, cx, head_cy, rx, ry)
        self._face(p, cx, head_cy, rx, ry, expr, blink)
        self._accessory(p, cx, head_cy, rx, ry)

    # ---------- 影子 ----------
    def _shadow(self, p, cx, w, h):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(30, 40, 60, 24)))
        _ellipse(p, cx, h * 0.965, w * 0.30, h * 0.032)

    # ---------- 头发：后层 ----------
    def _hair_back(self, p, cx, cy, rx, ry):
        p.setBrush(QBrush(HAIR_MAIN))
        p.setPen(QPen(HAIR_LINE, 1.6))
        _ellipse(p, cx, cy + ry * 0.06, rx * 1.06, ry * 1.04)

        # 双马尾：饱满圆润，根部宽、末端微翘
        for side in (-1, 1):
            ax = cx + side * rx * 0.90
            ay = cy - ry * 0.12
            path = QPainterPath()
            path.moveTo(ax, ay)
            path.cubicTo(
                cx + side * rx * 1.50, cy - ry * 0.02,
                cx + side * rx * 1.52, cy + ry * 0.88,
                cx + side * rx * 1.00, cy + ry * 1.20,
            )
            path.cubicTo(
                cx + side * rx * 0.64, cy + ry * 0.96,
                cx + side * rx * 0.64, cy + ry * 0.40,
                ax, ay,
            )
            p.setBrush(QBrush(HAIR_MAIN))
            p.setPen(QPen(HAIR_LINE, 1.4))
            p.drawPath(path)

            # 发束内侧阴影
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(HAIR_SHADE))
            _ellipse(p, cx + side * rx * 1.02, cy + ry * 0.80, rx * 0.16, ry * 0.30)

            # 马尾发圈（红）
            p.setBrush(QBrush(ACCENT))
            p.setPen(QPen(ACCENT_DARK, 1.2))
            _ellipse(p, cx + side * rx * 0.88, cy + ry * 0.10, rx * 0.115, ry * 0.105)

    # ---------- 身体 ----------
    def _body(self, p, cx, top, w, h, t):
        body_w = w * 0.24
        body_h = h * 0.28

        # 手臂（先画，被裙子遮住上缘）
        swing = 0.04 * body_h * (1 if int(t * 2) % 2 == 0 else -1)
        for side in (-1, 1):
            ax = cx + side * body_w * 0.56
            ay = top + body_h * 0.30 + swing
            p.setBrush(QBrush(SKIN))
            p.setPen(QPen(LINE, 1.3))
            _ellipse(p, ax, ay, body_w * 0.15, body_h * 0.20)

        # 连衣裙（上窄下宽）
        path = QPainterPath()
        path.moveTo(cx - body_w * 0.42, top)
        path.cubicTo(cx - body_w * 0.56, top + body_h * 0.35,
                     cx - body_w * 0.86, top + body_h * 0.66, cx - body_w * 0.84, top + body_h * 0.94)
        path.quadTo(cx, top + body_h * 1.04, cx + body_w * 0.84, top + body_h * 0.94)
        path.cubicTo(cx + body_w * 0.86, top + body_h * 0.66,
                     cx + body_w * 0.56, top + body_h * 0.35, cx + body_w * 0.42, top)
        path.closeSubpath()
        grad = QLinearGradient(0, top, 0, top + body_h)
        grad.setColorAt(0, CLOTH)
        grad.setColorAt(1, CLOTH_SHADE)
        p.setBrush(QBrush(grad))
        p.setPen(QPen(LINE, 1.4))
        p.drawPath(path)

        # 裙摆褶皱线
        p.setPen(QPen(CLOTH_SHADE, 1.4))
        for dx in (-0.42, 0.0, 0.42):
            x0 = cx + body_w * dx
            path = QPainterPath()
            path.moveTo(x0, top + body_h * 0.58)
            path.quadTo(x0 + body_w * 0.06, top + body_h * 0.80, x0 + body_w * 0.12, top + body_h * 0.95)
            p.drawPath(path)

        # 领口蝴蝶结
        self._bow(p, cx, top + body_h * 0.06, body_w * 0.30)

        # 鞋（裙摆下露出，白袜+红鞋）
        for side in (-1, 1):
            fx = cx + side * body_w * 0.22
            fy = top + body_h * 0.99
            p.setBrush(QBrush(SOCK))
            p.setPen(QPen(LINE, 1.1))
            _ellipse(p, fx, fy - body_h * 0.02, body_w * 0.13, body_h * 0.10)
            p.setBrush(QBrush(ACCENT))
            p.setPen(QPen(ACCENT_DARK, 1.2))
            _ellipse(p, fx, fy + body_h * 0.03, body_w * 0.16, body_h * 0.07)

    def _bow(self, p, cx, cy, size):
        p.setPen(QPen(ACCENT_DARK, 1.2))
        p.setBrush(QBrush(ACCENT))
        for side in (-1, 1):
            path = QPainterPath()
            path.moveTo(cx, cy)
            path.cubicTo(cx + side * size * 1.5, cy - size * 0.95,
                         cx + side * size * 1.7, cy + size * 0.60, cx, cy)
            path.closeSubpath()
            p.drawPath(path)
        p.setBrush(QBrush(ACCENT_DARK))
        _ellipse(p, cx, cy, size * 0.20, size * 0.24)

    # ---------- 头 ----------
    def _head(self, p, cx, cy, rx, ry):
        grad = QLinearGradient(0, cy - ry, 0, cy + ry)
        grad.setColorAt(0, QColor("#FFF2EA"))
        grad.setColorAt(1, SKIN)
        p.setBrush(QBrush(grad))
        p.setPen(QPen(LINE, 1.5))
        _ellipse(p, cx, cy, rx, ry)

    # ---------- 头发：前层 ----------
    def _hair_front(self, p, cx, cy, rx, ry):
        p.setBrush(QBrush(HAIR_MAIN))
        p.setPen(QPen(HAIR_LINE, 1.4))

        # 刘海：覆盖头顶，下缘平滑微弧 + 中间一撮尖发
        path = QPainterPath()
        path.moveTo(cx - rx * 1.02, cy - ry * 0.02)
        path.cubicTo(cx - rx * 1.06, cy - ry * 1.28, cx + rx * 1.06, cy - ry * 1.28, cx + rx * 1.02, cy - ry * 0.02)
        # 下缘：平滑弧形，中间一撮尖发下垂
        path.cubicTo(cx + rx * 0.80, cy + ry * 0.14, cx + rx * 0.42, cy + ry * 0.10, cx + rx * 0.14, cy + ry * 0.12)
        path.cubicTo(cx + rx * 0.06, cy + ry * 0.32, cx - rx * 0.02, cy + ry * 0.30, cx - rx * 0.12, cy + ry * 0.12)
        path.cubicTo(cx - rx * 0.48, cy + ry * 0.12, cx - rx * 0.84, cy + ry * 0.16, cx - rx * 1.02, cy - ry * 0.02)
        path.closeSubpath()
        p.drawPath(path)

        # 侧发（脸颊两缕，贴脸垂下）
        for side in (-1, 1):
            sp = QPainterPath()
            sp.moveTo(cx + side * rx * 0.98, cy - ry * 0.55)
            sp.cubicTo(cx + side * rx * 1.10, cy + ry * 0.40,
                       cx + side * rx * 0.92, cy + ry * 1.05, cx + side * rx * 0.74, cy + ry * 1.14)
            sp.cubicTo(cx + side * rx * 0.60, cy + ry * 0.90,
                       cx + side * rx * 0.74, cy + ry * 0.10, cx + side * rx * 0.92, cy - ry * 0.48)
            sp.closeSubpath()
            p.setBrush(QBrush(HAIR_MAIN))
            p.setPen(QPen(HAIR_LINE, 1.3))
            p.drawPath(sp)

        # 呆毛（明显向右弯曲的一撮）
        p.setPen(QPen(HAIR_LINE, 1.4))
        p.setBrush(QBrush(HAIR_MAIN))
        ah = QPainterPath()
        ah.moveTo(cx - rx * 0.07, cy - ry * 1.00)
        ah.cubicTo(cx + rx * 0.00, cy - ry * 1.72, cx + rx * 0.62, cy - ry * 1.50, cx + rx * 0.36, cy - ry * 0.96)
        ah.cubicTo(cx + rx * 0.18, cy - ry * 1.06, cx + rx * 0.04, cy - ry * 1.04, cx - rx * 0.07, cy - ry * 1.00)
        ah.closeSubpath()
        p.drawPath(ah)

    # ---------- 五官 ----------
    def _face(self, p, cx, cy, rx, ry, expr, blink):
        eye_dx = rx * 0.42
        eye_y = cy + ry * 0.22
        eye_rx = rx * 0.165
        eye_ry = ry * 0.26

        blush_alpha = {"shy": 175, "happy": 165, "angry": 95, "idle": 75}.get(expr, 60)

        # 腮红
        if blush_alpha:
            p.setPen(Qt.NoPen)
            bl = QColor(BLUSH)
            bl.setAlpha(blush_alpha)
            p.setBrush(QBrush(bl))
            for side in (-1, 1):
                _ellipse(p, cx + side * rx * 0.60, eye_y + ry * 0.24, rx * 0.16, ry * 0.11)

        for side in (-1, 1):
            ex = cx + side * eye_dx
            if blink or expr == "sleepy":
                p.setPen(QPen(EYE, 2.4))
                path = QPainterPath()
                path.moveTo(ex - eye_rx, eye_y)
                path.quadTo(ex, eye_y + ry * 0.10, ex + eye_rx, eye_y)
                p.drawPath(path)
                continue
            if expr == "happy":
                p.setPen(QPen(EYE, 2.8))
                path = QPainterPath()
                path.moveTo(ex - eye_rx, eye_y + eye_ry * 0.20)
                path.cubicTo(ex - eye_rx * 0.5, eye_y - eye_ry * 1.0,
                             ex + eye_rx * 0.5, eye_y - eye_ry * 1.0, ex + eye_rx, eye_y + eye_ry * 0.20)
                p.drawPath(path)
                continue

            # 普通眼
            p.setPen(Qt.NoPen)
            grad = QLinearGradient(0, eye_y - eye_ry, 0, eye_y + eye_ry)
            grad.setColorAt(0, EYE_TOP)
            grad.setColorAt(1, EYE)
            p.setBrush(QBrush(grad))
            _ellipse(p, ex, eye_y, eye_rx, eye_ry)
            # 高光
            p.setBrush(QBrush(QColor(255, 255, 255, 235)))
            _ellipse(p, ex - eye_rx * 0.42, eye_y - eye_ry * 0.50, eye_rx * 0.42, eye_ry * 0.36)
            p.setBrush(QBrush(QColor(255, 255, 255, 180)))
            _ellipse(p, ex + eye_rx * 0.30, eye_y + eye_ry * 0.34, eye_rx * 0.20, eye_ry * 0.16)
            # 上睫毛
            p.setPen(QPen(EYE, 2.6))
            path = QPainterPath()
            path.moveTo(ex - eye_rx * 1.08, eye_y - eye_ry * 0.42)
            path.cubicTo(ex - eye_rx * 0.5, eye_y - eye_ry * 1.32,
                         ex + eye_rx * 0.6, eye_y - eye_ry * 1.28, ex + eye_rx * 1.15, eye_y - eye_ry * 0.30)
            p.drawPath(path)

            # 眉毛
            p.setPen(QPen(EYE, 2.0))
            if expr == "angry":
                path = QPainterPath()
                path.moveTo(ex + side * eye_rx * 1.15, eye_y - eye_ry * 1.45)
                path.lineTo(ex - side * eye_rx * 0.90, eye_y - eye_ry * 1.02)
                p.drawPath(path)
            elif expr == "surprised":
                path = QPainterPath()
                path.moveTo(ex - eye_rx * 0.95, eye_y - eye_ry * 1.80)
                path.lineTo(ex + eye_rx * 0.95, eye_y - eye_ry * 1.80)
                p.drawPath(path)
            elif expr == "shy":
                path = QPainterPath()
                path.moveTo(ex - eye_rx * 0.95, eye_y - eye_ry * 1.25)
                path.lineTo(ex + eye_rx * 0.95, eye_y - eye_ry * 1.38)
                p.drawPath(path)
            else:
                path = QPainterPath()
                path.moveTo(ex - eye_rx * 0.90, eye_y - eye_ry * 1.32)
                path.quadTo(ex, eye_y - eye_ry * 1.60, ex + eye_rx * 0.90, eye_y - eye_ry * 1.30)
                p.drawPath(path)

        # 嘴
        p.setPen(QPen(EYE, 2.0))
        my = cy + ry * 0.60
        if expr == "happy":
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor("#E0738A")))
            path = QPainterPath()
            path.moveTo(cx - rx * 0.13, my - ry * 0.05)
            path.cubicTo(cx, my + ry * 0.30, cx, my + ry * 0.30, cx + rx * 0.13, my - ry * 0.05)
            path.closeSubpath()
            p.drawPath(path)
        elif expr == "angry":
            path = QPainterPath()
            path.moveTo(cx - rx * 0.09, my + ry * 0.05)
            path.cubicTo(cx, my - ry * 0.10, cx, my - ry * 0.10, cx + rx * 0.09, my + ry * 0.05)
            p.drawPath(path)
        elif expr == "surprised":
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor("#E0738A")))
            _ellipse(p, cx, my + ry * 0.02, rx * 0.07, ry * 0.09)
        elif expr == "shy":
            path = QPainterPath()
            path.moveTo(cx - rx * 0.08, my)
            path.cubicTo(cx - rx * 0.03, my + ry * 0.12, cx + rx * 0.03, my + ry * 0.12, cx + rx * 0.08, my)
            p.drawPath(path)
        else:
            path = QPainterPath()
            path.moveTo(cx - rx * 0.08, my - ry * 0.01)
            path.cubicTo(cx - rx * 0.02, my + ry * 0.13, cx + rx * 0.02, my + ry * 0.13, cx + rx * 0.08, my - ry * 0.01)
            p.drawPath(path)

    # ---------- 发饰：左右鬓角红色发夹（通用元素） ----------
    def _accessory(self, p, cx, cy, rx, ry):
        for side in (-1, 1):
            x = cx + side * rx * 0.60
            y = cy - ry * 0.30
            p.save()
            p.translate(x, y)
            p.rotate(side * 18)
            p.setPen(QPen(ACCENT_DARK, 1.2))
            p.setBrush(QBrush(ACCENT))
            p.drawRoundedRect(QRectF(-rx * 0.13, -ry * 0.055, rx * 0.26, ry * 0.11), 3, 3)
            p.setPen(QPen(ACCENT_DARK, 1.0))
            p.drawLine(QPointF(-rx * 0.02, -ry * 0.055), QPointF(-rx * 0.02, ry * 0.055))
            p.restore()
