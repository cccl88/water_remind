"""主窗口：进度、设置、统计"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTime, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QTimeEdit,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QAbstractSpinBox,
    QGraphicsDropShadowEffect,
    QApplication,
)
from PySide6.QtGui import QColor

from .theme import get, qss
from .widgets import RingProgress, BarChart, Switch, water_drop_pixmap


def _card(theme: str) -> QWidget:
    w = QWidget()
    w.setObjectName("card")
    return w


def _row_label(text: str, value: str):
    box = QWidget()
    lay = QHBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    l = QLabel(text)
    l.setObjectName("sub")
    v = QLabel(value)
    v.setObjectName("value")
    lay.addWidget(l)
    lay.addStretch(1)
    lay.addWidget(v)
    return box, v


class MainWindow(QMainWindow):
    themeChanged = Signal(str)
    quitRequested = Signal()

    def __init__(self, controller):
        super().__init__()
        self.ctrl = controller
        self.cfg = controller.config
        self.theme = self.cfg.theme

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("喝水提醒")
        self.setFixedWidth(430)

        screen = QApplication.primaryScreen().availableGeometry()
        self.setFixedHeight(min(760, screen.height() - 60))

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(0)

        # ---------- 标题栏 ----------
        bar = QWidget()
        bar.setFixedHeight(34)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(6, 0, 4, 0)
        icon = QLabel()
        icon.setPixmap(water_drop_pixmap(24, get(self.theme)["primary"], dark=self.theme == "dark"))
        self.icon_label = icon
        name = QLabel("喝水提醒")
        name.setObjectName("appname")
        self.btn_min = QPushButton("—")
        self.btn_min.setObjectName("titlebtn")
        self.btn_min.setFixedSize(26, 22)
        self.btn_min.clicked.connect(self.hide)
        self.btn_close = QPushButton("×")
        self.btn_close.setObjectName("titlebtn")
        self.btn_close.setObjectName("closebtn")
        self.btn_close.setFixedSize(26, 22)
        self.btn_close.clicked.connect(self.hide)
        bl.addWidget(icon)
        bl.addSpacing(4)
        bl.addWidget(name)
        bl.addStretch(1)
        bl.addWidget(self.btn_min)
        bl.addWidget(self.btn_close)
        outer.addWidget(bar)

        # 标题栏拖动
        bar.mousePressEvent = self._start_move
        bar.mouseMoveEvent = self._do_move

        # ---------- 滚动内容 ----------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(6, 4, 6, 10)
        cl.setSpacing(12)

        # 进度环
        ring_wrap = QWidget()
        rl = QVBoxLayout(ring_wrap)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(6)
        self.ring = RingProgress(theme=self.theme)
        rl.addWidget(self.ring, 0, Qt.AlignCenter)
        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("sub")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        rl.addWidget(self.lbl_status)
        cl.addWidget(ring_wrap)

        # 快捷操作
        act = QWidget()
        al = QHBoxLayout(act)
        al.setContentsMargins(0, 0, 0, 0)
        al.setSpacing(10)
        self.btn_drink = QPushButton("我喝了一杯")
        self.btn_drink.setObjectName("primary")
        self.btn_drink.setCursor(Qt.PointingHandCursor)
        self.btn_drink.clicked.connect(self.ctrl.drink)
        self.btn_undo = QPushButton("撤销")
        self.btn_undo.setObjectName("ghost")
        self.btn_undo.setFixedWidth(72)
        self.btn_undo.setCursor(Qt.PointingHandCursor)
        self.btn_undo.clicked.connect(self.ctrl.undo)
        al.addWidget(self.btn_drink, 1)
        al.addWidget(self.btn_undo)
        cl.addWidget(act)

        # ---- 提醒设置 ----
        c1 = _card(self.theme)
        l1 = QVBoxLayout(c1)
        l1.setContentsMargins(14, 12, 14, 14)
        l1.setSpacing(8)
        s = QLabel("提醒设置")
        s.setObjectName("section")
        l1.addWidget(s)

        self.interval_row, self.lbl_interval = _row_label("提醒间隔", f"{self.cfg.interval_min} 分钟")
        l1.addWidget(self.interval_row)
        self.sl_interval = self._slider(5, 180, 5, self.cfg.interval_min)
        self.sl_interval.valueChanged.connect(self._on_interval)
        l1.addWidget(self.sl_interval)

        tr = QWidget()
        tl = QHBoxLayout(tr)
        tl.setContentsMargins(0, 4, 0, 0)
        tl.addWidget(QLabel("提醒时段", objectName="sub"))
        tl.addStretch(1)
        self.time_from = QTimeEdit(QTime.fromString(self.cfg.active_from, "HH:mm"))
        self.time_to = QTimeEdit(QTime.fromString(self.cfg.active_to, "HH:mm"))
        for t in (self.time_from, self.time_to):
            t.setDisplayFormat("HH:mm")
            t.setFixedWidth(96)
            t.setAlignment(Qt.AlignCenter)
            t.timeChanged.connect(self._on_times)
        tl.addWidget(self.time_from)
        tl.addWidget(QLabel("—", objectName="sub"))
        tl.addWidget(self.time_to)
        l1.addWidget(tr)

        self.snooze_row, self.lbl_snooze = _row_label("稍后再说顺延", f"{self.cfg.snooze_min} 分钟")
        l1.addWidget(self.snooze_row)
        self.sl_snooze = self._slider(5, 60, 5, self.cfg.snooze_min)
        self.sl_snooze.valueChanged.connect(self._on_snooze)
        l1.addWidget(self.sl_snooze)

        en = QWidget()
        enl = QHBoxLayout(en)
        enl.setContentsMargins(0, 4, 0, 0)
        enl.addWidget(QLabel("启用提醒", objectName="sub"))
        enl.addStretch(1)
        self.sw_enable = Switch(theme=self.theme, checked=self.cfg.enabled)
        self.sw_enable.toggled.connect(self._on_enable)
        enl.addWidget(self.sw_enable)
        l1.addWidget(en)
        cl.addWidget(c1)

        # ---- 饮水设置 ----
        c2 = _card(self.theme)
        l2 = QVBoxLayout(c2)
        l2.setContentsMargins(14, 12, 14, 14)
        l2.setSpacing(8)
        l2.addWidget(QLabel("饮水设置", objectName="section"))

        self.cup_row, self.lbl_cup = _row_label("每杯水量", f"{self.cfg.cup_ml} ml")
        l2.addWidget(self.cup_row)
        self.sl_cup = self._slider(100, 500, 50, self.cfg.cup_ml)
        self.sl_cup.valueChanged.connect(self._on_cup)
        l2.addWidget(self.sl_cup)

        self.goal_row, self.lbl_goal = _row_label("每日目标", f"{self.cfg.goal_ml} ml")
        l2.addWidget(self.goal_row)
        self.sl_goal = self._slider(500, 4000, 100, self.cfg.goal_ml)
        self.sl_goal.valueChanged.connect(self._on_goal)
        l2.addWidget(self.sl_goal)
        cl.addWidget(c2)

        # ---- 统计 ----
        c3 = _card(self.theme)
        l3 = QVBoxLayout(c3)
        l3.setContentsMargins(14, 12, 14, 12)
        l3.setSpacing(8)
        l3.addWidget(QLabel("最近 7 天", objectName="section"))
        self.chart = BarChart(theme=self.theme)
        l3.addWidget(self.chart)
        cl.addWidget(c3)

        # ---- 其他 ----
        c4 = _card(self.theme)
        l4 = QVBoxLayout(c4)
        l4.setContentsMargins(14, 12, 14, 12)
        l4.setSpacing(8)
        l4.addWidget(QLabel("其他", objectName="section"))

        for text, sw_name, checked, cb in (
            ("开机自动启动", "sw_autostart", self.cfg.auto_start, self._on_autostart),
            ("深色模式", "sw_dark", self.theme == "dark", self._on_dark),
        ):
            row = QWidget()
            rl2 = QHBoxLayout(row)
            rl2.setContentsMargins(0, 0, 0, 0)
            rl2.addWidget(QLabel(text, objectName="sub"))
            rl2.addStretch(1)
            sw = Switch(theme=self.theme, checked=checked)
            sw.toggled.connect(cb)
            setattr(self, sw_name, sw)
            rl2.addWidget(sw)
            l4.addWidget(row)

        note = QLabel("静默提醒 · 本应用不播放任何提示音")
        note.setObjectName("sub")
        l4.addWidget(note)
        cl.addWidget(c4)

        # 底部状态
        foot = QWidget()
        fl = QVBoxLayout(foot)
        fl.setContentsMargins(0, 2, 0, 0)
        fl.setSpacing(8)
        self.lbl_next = QLabel("")
        self.lbl_next.setObjectName("sub")
        self.lbl_next.setAlignment(Qt.AlignCenter)
        fl.addWidget(self.lbl_next)

        fr = QHBoxLayout()
        fr.setSpacing(8)
        self.btn_pause = QPushButton("暂停提醒")
        self.btn_pause.setObjectName("ghost")
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.clicked.connect(self.ctrl.toggle_pause)
        self.btn_test = QPushButton("测试提醒")
        self.btn_test.setObjectName("ghost")
        self.btn_test.setCursor(Qt.PointingHandCursor)
        self.btn_test.clicked.connect(self.ctrl.show_reminder_now)
        fr.addWidget(self.btn_pause, 1)
        fr.addWidget(self.btn_test, 1)
        fl.addLayout(fr)
        cl.addWidget(foot)

        cl.addStretch(1)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 60))
        root.setGraphicsEffect(shadow)

        self.apply_theme(self.theme)

    # ---------- 工具 ----------
    def _slider(self, lo, hi, step, val):
        sl = QSlider(Qt.Horizontal)
        sl.setRange(lo, hi)
        sl.setSingleStep(step)
        sl.setPageStep(step)
        sl.setValue(val)
        sl.setFixedHeight(20)
        return sl

    def _start_move(self, e):
        if e.button() == Qt.LeftButton:
            self.window().windowHandle().startSystemMove()

    def _do_move(self, e):
        pass

    # ---------- 设置回调 ----------
    def _on_interval(self, v):
        self.lbl_interval.setText(f"{v} 分钟")
        self.cfg.interval_min = v
        self.ctrl.on_interval_changed()

    def _on_snooze(self, v):
        self.lbl_snooze.setText(f"{v} 分钟")
        self.cfg.snooze_min = v
        self.ctrl.save_config()

    def _on_cup(self, v):
        self.lbl_cup.setText(f"{v} ml")
        self.cfg.cup_ml = v
        self.ctrl.on_cup_changed()

    def _on_goal(self, v):
        self.lbl_goal.setText(f"{v} ml")
        self.cfg.goal_ml = v
        self.ctrl.on_goal_changed()

    def _on_times(self, _):
        self.cfg.active_from = self.time_from.time().toString("HH:mm")
        self.cfg.active_to = self.time_to.time().toString("HH:mm")
        self.ctrl.save_config()

    def _on_enable(self, v):
        self.cfg.enabled = v
        self.ctrl.on_enable_changed(v)

    def _on_autostart(self, v):
        self.cfg.auto_start = v
        self.ctrl.set_auto_start(v)

    def _on_dark(self, v):
        self.cfg.theme = "dark" if v else "light"
        self.ctrl.save_config()
        self.themeChanged.emit(self.cfg.theme)

    # ---------- 主题 ----------
    def apply_theme(self, theme: str):
        self.theme = theme
        self.setStyleSheet(qss(theme))
        self.ring.theme = theme
        self.chart.theme = theme
        self.sw_enable.theme = theme
        self.sw_autostart.theme = theme
        self.sw_dark.theme = theme
        self.icon_label.setPixmap(water_drop_pixmap(24, get(theme)["primary"], dark=theme == "dark"))
        self.update()

    def refresh(self, total_ml: int, cups: int, next_text: str, status_text: str, paused: bool):
        goal = self.cfg.goal_ml
        self.ring.current_ml = total_ml
        self.ring.goal_ml = goal
        self.ring.setValue(total_ml / goal if goal else 0)
        self.lbl_status.setText(status_text)
        self.lbl_next.setText(next_text)
        self.btn_drink.setText(f"我喝了一杯 +{self.cfg.cup_ml}ml")
        self.btn_pause.setText("继续提醒" if paused else "暂停提醒")
        self.chart.setData(self.ctrl.store.last_days(7), goal)
        self.btn_undo.setEnabled(cups > 0)
