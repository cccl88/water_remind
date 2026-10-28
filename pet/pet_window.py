"""桌宠窗口：透明置顶、可拖动、呼吸/眨眼动画、点击互动"""
from __future__ import annotations

import random

from PySide6.QtCore import Qt, QTimer, QPoint, QRectF
from PySide6.QtGui import QPainter, QRegion, QCursor
from PySide6.QtWidgets import QWidget, QMenu, QApplication

from .character import Character
from .bubble import PetBubble
from ui.theme import get


class PetWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.ctrl = controller
        self.char = Character()
        self.expr = "idle"
        self._blink = False
        self._t = 0.0
        self._jump_phase = 0.0   # 跳跃进度（>0 表示正在跳）
        self._jump_total = 0.0
        self.bubble = None
        self._drag_start = None
        self._moved = False

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.setFixedSize(200, 250)

        self._anim = QTimer(self)
        self._anim.setInterval(40)
        self._anim.timeout.connect(self._on_anim)
        self._anim.start()

        self._plan_blink()

        # 初始位置：屏幕右下角偏上
        pos = self.ctrl.config.pet_pos
        if pos and len(pos) == 2:
            self.move(*pos)
        else:
            geo = QApplication.primaryScreen().availableGeometry()
            self.move(geo.right() - self.width() - 40, geo.bottom() - self.height() - 60)

    # ---------- 动画 ----------
    def _on_anim(self):
        self._t += 0.04
        if self._jump_total > 0:
            self._jump_phase += 1
            if self._jump_phase > 24:
                self._jump_total = 0
                self._jump_phase = 0
        self.update()

    def _bob_offset(self) -> float:
        import math
        bob = math.sin(self._t * 2.2) * 2.2
        if self._jump_total > 0:
            # 24 帧跳跃：先快速上升再落下
            import math as m
            frac = self._jump_phase / 24.0
            bob -= m.sin(frac * m.pi) * 16
        return bob

    def _plan_blink(self):
        QTimer.singleShot(random.randint(2200, 5600), self._do_blink)

    def _do_blink(self):
        self._blink = True
        self.update()
        QTimer.singleShot(130, self._end_blink)
        self._plan_blink()

    def _end_blink(self):
        self._blink = False
        self.update()

    # ---------- 外观 ----------
    def paintEvent(self, event):
        p = QPainter(self)
        p.translate(0, self._bob_offset())
        theme = self.ctrl.config.theme
        self.char.paint(p, self.width(), self.height(), expr=self.expr, t=self._t,
                        blink=self._blink, theme=theme)

    def _build_mask(self):
        """限制点击区域到角色轮廓（透明区域不拦截鼠标）"""
        w, h = self.width(), self.height()
        cx, cy = w * 0.5, h * 0.335
        rx, ry = w * 0.335, h * 0.26
        region = QRegion()
        # 头
        region += QRegion(int(cx - rx * 1.0), int(cy - ry * 1.0), int(rx * 2), int(ry * 2), QRegion.Ellipse)
        # 身体
        region += QRegion(int(cx - w * 0.13), int(cy + ry * 0.78), int(w * 0.26), int(h * 0.33))
        # 双马尾
        for side in (-1, 1):
            region += QRegion(
                int(cx + side * rx * 0.55 - rx * 0.45), int(cy - ry * 0.15),
                int(rx * 0.95), int(ry * 1.5), QRegion.Ellipse,
            )
        self.setMask(region)

    def showEvent(self, e):
        self._build_mask()
        super().showEvent(e)

    def resizeEvent(self, e):
        self._build_mask()
        super().resizeEvent(e)

    # ---------- 交互 ----------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_start = e.globalPosition().toPoint() - self.pos()
            self._moved = False

    def mouseMoveEvent(self, e):
        if self._drag_start is not None and e.buttons() & Qt.LeftButton:
            self._moved = True
            self.move(e.globalPosition().toPoint() - self._drag_start)
            self._reposition_bubble()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            moved = self._moved
            self._drag_start = None
            if not moved:
                self.ctrl.on_pet_clicked()
        self._save_pos()

    def _save_pos(self):
        self.ctrl.config.pet_pos = [self.x(), self.y()]
        self.ctrl.config.save()

    def contextMenuEvent(self, e):
        c = get(self.ctrl.config.theme)
        menu = QMenu(self)
        menu.setStyleSheet(
            f"QMenu {{ background: {c['card']}; border: 1px solid {c['border']}; border-radius: 10px; padding: 4px; }}"
            f"QMenu::item {{ color: {c['text']}; padding: 6px 18px; border-radius: 6px; }}"
            f"QMenu::item:selected {{ background: {c['primary_soft']}; color: {c['primary']}; }}"
        )
        ac_drink = menu.addAction("喝了")
        ac_snooze = menu.addAction("稍后再说")
        menu.addSeparator()
        ac_pause = menu.addAction("继续提醒" if self.ctrl.paused else "暂停提醒")
        ac_settings = menu.addAction("打开设置")
        ac_hide = menu.addAction("藏起来")
        menu.addSeparator()
        ac_quit = menu.addAction("退出")

        act = menu.exec(QCursor.pos())
        if act == ac_drink:
            self.ctrl.drink()
        elif act == ac_snooze:
            self.ctrl.snooze()
        elif act == ac_pause:
            self.ctrl.toggle_pause()
        elif act == ac_settings:
            self.ctrl.show_window()
        elif act == ac_hide:
            self.ctrl.toggle_pet(False)
        elif act == ac_quit:
            self.ctrl.quit()

    # ---------- 表情与反应 ----------
    def set_expression(self, expr: str, hold_ms: int = 0):
        self.expr = expr
        self.update()
        if hold_ms:
            QTimer.singleShot(hold_ms, lambda: self.set_expression("idle"))

    def jump(self, cycles: float = 1.0):
        self._jump_phase = 0
        self._jump_total = 24 * cycles

    # ---------- 气泡 ----------
    def show_bubble(self, text: str, with_actions: bool = False, auto_close_ms: int = 12000):
        self.close_bubble()
        b = PetBubble(text, theme=self.ctrl.config.theme, with_actions=with_actions)
        if with_actions:
            b.drinkClicked.connect(self.ctrl.drink)
            b.snoozeClicked.connect(self.ctrl.snooze)
            b.skipClicked.connect(self.ctrl.skip)
        self.bubble = b
        b.show()
        self._reposition_bubble()
        if auto_close_ms:
            b.start_auto_close(auto_close_ms)
        return b

    def close_bubble(self):
        if self.bubble is not None:
            try:
                self.bubble.close()
                self.bubble.deleteLater()
            except Exception:
                pass
            self.bubble = None

    def _reposition_bubble(self):
        if self.bubble is None:
            return
        b = self.bubble
        geo = QApplication.primaryScreen().availableGeometry()
        x = self.x() + (self.width() - b.width()) // 2
        x = max(geo.left() + 8, min(x, geo.right() - b.width() - 8))
        y = self.y() - b.height() - 4
        if y < geo.top() + 8:
            y = self.y() + self.height() + 4
        b.move(x, y)

    # ---------- 桌宠 API ----------
    def remind(self, text: str):
        """到点提醒：气泡 + 表情 + 跳跃"""
        self.show()
        self.set_expression("surprised", hold_ms=1800)
        self.jump(1.0)
        self.show_bubble(text, with_actions=True, auto_close_ms=0)

    def react(self, scene: str, text: str):
        """普通反应：表情 + 无按钮台词气泡"""
        expr = {
            "greet": "happy", "drink": "happy", "click": "shy",
            "snooze": "idle", "skip": "angry", "pause": "sleepy",
        }.get(scene, "idle")
        self.set_expression(expr, hold_ms=2500)
        self.show_bubble(text, with_actions=False, auto_close_ms=4000)

    def hide_pet(self):
        self.close_bubble()
        self.hide()

    def show_pet(self):
        self.show()
