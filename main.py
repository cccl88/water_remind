"""喝水提醒 —— Windows 桌面应用入口
特性：可自定义提醒间隔、静默无提示音、系统托盘常驻、饮水统计。
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

from PySide6.QtCore import Qt, QTimer, QObject, QTime
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtNetwork import QLocalServer, QLocalSocket

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import Config, set_auto_start, is_auto_start  # noqa: E402
from core.store import Store  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402
from ui.popup import ReminderPopup  # noqa: E402
from ui.widgets import water_drop_pixmap  # noqa: E402
from ui.theme import get  # noqa: E402

SINGLE_KEY = "WaterReminder_SingleInstance_v1"


def parse_hm(s: str):
    h, m = (s or "00:00").split(":")
    return int(h), int(m)


class Controller(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.config = Config.load()
        self.store = Store()
        self.paused = False
        self.popup = None
        self.next_remind = datetime.now() + timedelta(minutes=self.config.interval_min)

        self.window = MainWindow(self)
        self.window.themeChanged.connect(self.apply_theme)

        self._build_tray()

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        # 开机自启状态同步（可能被外部删除）
        self.config.auto_start = is_auto_start()

        self.refresh_ui()

    # ---------------- 托盘 ----------------
    def _build_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("喝水提醒")
        self.tray.activated.connect(self._tray_activated)
        self._refresh_tray_icon()
        menu = QMenu()
        self.ac_show = QAction("显示窗口", menu)
        self.ac_show.triggered.connect(self.show_window)
        self.ac_pause = QAction("暂停提醒", menu)
        self.ac_pause.triggered.connect(self.toggle_pause)
        self.ac_drink = QAction("我喝了一杯", menu)
        self.ac_drink.triggered.connect(self.drink)
        ac_quit = QAction("退出", menu)
        ac_quit.triggered.connect(self.quit)
        menu.addAction(self.ac_show)
        menu.addAction(self.ac_pause)
        menu.addAction(self.ac_drink)
        menu.addSeparator()
        menu.addAction(ac_quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def _refresh_tray_icon(self):
        c = get(self.config.theme)
        self.tray.setIcon(QIcon(water_drop_pixmap(64, c["primary"], dark=self.config.theme == "dark")))
        self.app.setWindowIcon(QIcon(water_drop_pixmap(64, c["primary"], dark=self.config.theme == "dark")))

    def _tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_window()

    def show_window(self):
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    # ---------------- 时间 ----------------
    def in_active(self, now: datetime) -> bool:
        cfg = self.config
        fh, fm = parse_hm(cfg.active_from)
        th, tm = parse_hm(cfg.active_to)
        start = now.replace(hour=fh, minute=fm, second=0, microsecond=0)
        end = now.replace(hour=th, minute=tm, second=0, microsecond=0)
        if start <= end:
            return start <= now <= end
        return now >= start or now <= end

    def next_active_start(self, now: datetime) -> datetime:
        fh, fm = parse_hm(self.config.active_from)
        start = now.replace(hour=fh, minute=fm, second=0, microsecond=0)
        if now < start:
            return start
        return start + timedelta(days=1)

    def schedule_next(self, minutes: int | None = None):
        m = minutes if minutes is not None else self.config.interval_min
        self.next_remind = datetime.now() + timedelta(minutes=max(1, m))

    # ---------------- 计时候 ----------------
    def tick(self):
        now = datetime.now()
        if self.config.enabled and not self.paused and self.popup is None:
            if self.in_active(now):
                if now >= self.next_remind:
                    self.show_reminder()
            else:
                # 非提醒时段：静默等待到时段开始
                self.next_remind = self.next_active_start(now)
        self.refresh_ui()

    def countdown_text(self) -> str:
        if self.popup is not None:
            return "提醒中 · 请点击弹窗处理"
        if not self.config.enabled:
            return "提醒已关闭（可在「提醒设置」中开启）"
        if self.paused:
            return "提醒已暂停"
        if not self.in_active(datetime.now()):
            return f"当前不在提醒时段（{self.config.active_from} - {self.config.active_to}）"
        delta = self.next_remind - datetime.now()
        if delta.total_seconds() <= 0:
            return "即将提醒…"
        total = int(delta.total_seconds())
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        hhmm = self.next_remind.strftime("%H:%M")
        left = f"{h} 小时 {m} 分" if h else f"{m} 分 {s} 秒"
        return f"下次提醒 {hhmm} · 还有 {left}"

    # ---------------- 提醒弹窗（静默，无声音） ----------------
    def show_reminder(self):
        if self.popup is not None:
            return
        cfg = self.config
        elapsed = self._elapsed_text()
        total = self.store.today_total()
        p = ReminderPopup(
            theme=cfg.theme,
            cup_ml=cfg.cup_ml,
            snooze_min=cfg.snooze_min,
            elapsed_text=elapsed,
            today_text=f"今日已喝 {total} ml / {cfg.goal_ml} ml",
        )
        p.drinkClicked.connect(self.drink)
        p.snoozeClicked.connect(self.snooze)
        p.skipClicked.connect(self.skip)
        self.popup = p
        p.show_at_top()

    def show_reminder_now(self):
        """测试提醒"""
        self.show_reminder()

    def _elapsed_text(self) -> str:
        cups = self.store.today_cups()
        if not cups:
            return "今天还没喝水，先来一杯吧"
        try:
            h, m = cups[-1]["time"].split(":")
            last = datetime.now().replace(hour=int(h), minute=int(m), second=0, microsecond=0)
            mins = int((datetime.now() - last).total_seconds() // 60)
            if mins >= 60:
                h, m = divmod(mins, 60)
                return f"距上次喝水已 {h} 小时 {m} 分"
            return f"距上次喝水已 {mins} 分钟"
        except Exception:
            return "该喝水啦"

    def _close_popup(self):
        if self.popup is not None:
            p = self.popup
            self.popup = None
            try:
                p.close()
                p.deleteLater()
            except Exception:
                pass

    # ---------------- 行为 ----------------
    def drink(self):
        self.store.add(self.config.cup_ml)
        self._close_popup()
        self.schedule_next()
        self.refresh_ui()
        self.notify_tray(f"已记录 {self.config.cup_ml} ml，真棒！")

    def undo(self):
        if self.store.undo():
            self.refresh_ui()

    def snooze(self):
        self._close_popup()
        self.schedule_next(self.config.snooze_min)
        self.refresh_ui()

    def skip(self):
        self._close_popup()
        self.schedule_next()
        self.refresh_ui()

    def toggle_pause(self):
        self.paused = not self.paused
        if not self.paused:
            self.schedule_next()
        self.refresh_ui()

    def notify_tray(self, msg: str):
        self.tray.showMessage("喝水提醒", msg, QSystemTrayIcon.NoIcon, 2500)

    # ---------------- 设置变更 ----------------
    def on_interval_changed(self):
        self.schedule_next()
        self.save_config()
        self.refresh_ui()

    def on_cup_changed(self):
        self.save_config()
        self.refresh_ui()

    def on_goal_changed(self):
        self.save_config()
        self.refresh_ui()

    def on_enable_changed(self, v: bool):
        if v:
            self.schedule_next()
        self.save_config()
        self.refresh_ui()

    def set_auto_start(self, v: bool):
        set_auto_start(v)
        self.config.auto_start = is_auto_start()
        self.save_config()

    def save_config(self):
        self.config.save()

    def apply_theme(self, theme: str):
        self.window.apply_theme(theme)
        self._refresh_tray_icon()
        if self.popup is not None:
            pass

    # ---------------- 界面刷新 ----------------
    def refresh_ui(self):
        total = self.store.today_total()
        cups = len(self.store.today_cups())
        streak = self.store.streak(self.config.goal_ml)
        status = f"今日 {total} ml · {cups} 杯"
        if streak > 0:
            status += f" · 连续达标 {streak} 天"
        self.window.refresh(total, cups, self.countdown_text(), status, self.paused)
        self.ac_pause.setText("继续提醒" if self.paused else "暂停提醒")
        self.tray.setToolTip(f"喝水提醒 · 今日 {total}/{self.config.goal_ml} ml")

    def quit(self):
        self._close_popup()
        self.config.save()
        self.tray.hide()
        self.app.quit()


def _selftest(app: QApplication, demo: bool = False):
    """自检模式：渲染界面截图并校验核心逻辑（--selftest / --selftest=demo）
    不写入任何饮水记录，不影响正在运行的实例。demo 模式渲染演示数据截图（用于 README）。
    """
    import time

    ctrl = Controller(app)
    ok = []

    def settle(sec=0.9):
        t0 = time.time()
        while time.time() - t0 < sec:
            app.processEvents()
            time.sleep(0.05)

    for theme, main_png, popup_png in (
        ("light", "preview_main.png", "preview_popup.png"),
        ("dark", "preview_main_dark.png", "preview_popup_dark.png"),
    ):
        ctrl.config.theme = theme
        ctrl.apply_theme(theme)
        ctrl.window.show()
        settle()
        if demo:
            # 演示数据：仅内存伪造（blockSignals 防止触发保存），不污染用户配置
            ctrl.config.interval_min, ctrl.config.cup_ml, ctrl.config.goal_ml = 45, 250, 2000
            ctrl.config.active_from, ctrl.config.active_to = "08:00", "22:00"
            ctrl.config.snooze_min = 10
            w = ctrl.window
            for sl, v in ((w.sl_interval, 45), (w.sl_snooze, 10), (w.sl_cup, 250), (w.sl_goal, 2000)):
                sl.blockSignals(True)
                sl.setValue(v)
                sl.blockSignals(False)
            w.lbl_interval.setText("45 分钟")
            w.lbl_snooze.setText("10 分钟")
            w.lbl_cup.setText("250 ml")
            w.lbl_goal.setText("2000 ml")
            w.time_from.blockSignals(True)
            w.time_from.setTime(QTime(8, 0))
            w.time_from.blockSignals(False)
            w.time_to.blockSignals(True)
            w.time_to.setTime(QTime(22, 0))
            w.time_to.blockSignals(False)
            ctrl.window.refresh(
                1600, 6, "下次提醒 20:30 · 还有 35 分", "今日 1600 ml · 6 杯 · 连续达标 2 天", False
            )
            today = datetime.now().date()
            demo_days = [
                (today - timedelta(days=i), v)
                for i, v in zip(range(6, -1, -1), (1200, 2100, 1800, 900, 2200, 1500, 1600))
            ]
            ctrl.window.chart.setData(demo_days, 2000)
            settle(0.5)
        ctrl.window.grab().save(os.path.join("assets", main_png))
        ok.append(main_png)

        if demo:
            p = ReminderPopup(
                theme=theme, cup_ml=250, snooze_min=10,
                elapsed_text="距上次喝水已 47 分钟", today_text="今日已喝 1600 ml / 2000 ml",
            )
            p.show_at_top()
            settle(0.7)
            p.grab().save(os.path.join("assets", popup_png))
            ok.append(popup_png)
            p.close()
            p.deleteLater()
        else:
            ctrl.show_reminder()
            settle(0.7)
            if ctrl.popup is not None:
                ctrl.popup.grab().save(os.path.join("assets", popup_png))
                ok.append(popup_png)
            ctrl.skip()

    # 计时逻辑：到点必须触发（临时放开提醒时段，避免当前时刻不在时段内误判）
    ctrl.config.active_from, ctrl.config.active_to = "00:00", "23:59"
    ctrl.next_remind = datetime.now() - timedelta(seconds=1)
    ctrl.tick()
    assert ctrl.popup is not None, "到点未触发提醒"
    ctrl.skip()

    ctrl.tray.hide()
    msg = "SELFTEST_OK: " + ", ".join(ok)
    try:
        with open("_selftest.log", "w", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass
    try:
        print(msg)
    except Exception:
        pass
    return 0


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("喝水提醒")

    if "--selftest" in sys.argv or "--selftest=demo" in sys.argv:
        sys.exit(_selftest(app, demo="--selftest=demo" in sys.argv))

    # 单实例：已运行则唤醒旧窗口并退出
    sock = QLocalSocket()
    sock.connectToServer(SINGLE_KEY)
    if sock.waitForConnected(200):
        sock.write(b"show")
        sock.flush()
        sock.waitForBytesWritten(200)
        sock.disconnectFromServer()
        sys.exit(0)

    server = QLocalServer()
    QLocalServer.removeServer(SINGLE_KEY)
    server.listen(SINGLE_KEY)

    ctrl = Controller(app)
    server.newConnection.connect(lambda: ctrl.show_window())

    ctrl.show_window()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
