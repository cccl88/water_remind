"""离屏冒烟测试：构造界面、渲染截图、验证核心逻辑（不进入常驻循环）"""
import os
import sys
from datetime import datetime, timedelta

os.environ.setdefault("QT_QPA_PLATFORM", "windows")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

import main as M

app = QApplication([])

ctrl = M.Controller(app)
cfg = ctrl.config

# 造一点示例数据
today = datetime.now()
for t, ml in ((9, 250), (11, 250), (14, 300)):
    ctrl.store.add(ml, when=today.replace(hour=t, minute=0))

ctrl.refresh_ui()
ctrl.window.show()
ctrl.window.resize(430, 760)


def shot():
    app.processEvents()
    os.makedirs("assets", exist_ok=True)
    ctrl.window.grab().save("assets/preview_main.png")
    print("main window size:", ctrl.window.width(), ctrl.window.height())
    print("countdown:", ctrl.countdown_text())
    print("today total:", ctrl.store.today_total())

    # 提醒弹窗（等入场动画结束再截图）
    ctrl.show_reminder()
    for _ in range(6):
        app.processEvents()
        QTimer.singleShot(0, lambda: None)
    import time
    t0 = time.time()
    while time.time() - t0 < 0.5:
        app.processEvents()
        time.sleep(0.05)
    if ctrl.popup is not None:
        ctrl.popup.grab().save("assets/preview_popup.png")
        print("popup ok")

    # 逻辑校验：关闭弹窗后到点应触发提醒
    assert isinstance(ctrl.in_active(datetime.now()), bool)
    ctrl.skip()
    assert ctrl.popup is None, "popup 未关闭"
    ctrl.next_remind = datetime.now() - timedelta(seconds=1)
    fired = {"n": 0}
    orig = ctrl.show_reminder
    ctrl.show_reminder = lambda: fired.__setitem__("n", fired["n"] + 1) or orig()
    ctrl.tick()
    print("reminder fired:", fired["n"] >= 1)

    before = ctrl.store.today_total()
    ctrl.drink()
    print("drink +250 ->", before, "=>", ctrl.store.today_total())
    ctrl.undo()
    print("undo ->", ctrl.store.today_total())
    print("streak:", ctrl.store.streak(cfg.goal_ml))

    # 深色主题验证
    ctrl.config.theme = "dark"
    ctrl.apply_theme("dark")
    ctrl.window.show()
    app.processEvents()
    ctrl.window.grab().save("assets/preview_main_dark.png")
    ctrl.show_reminder()
    t0 = time.time()
    while time.time() - t0 < 0.5:
        app.processEvents()
        time.sleep(0.05)
    if ctrl.popup is not None:
        ctrl.popup.grab().save("assets/preview_popup_dark.png")
    ctrl.skip()

    print("SMOKE_OK")
    app.quit()


QTimer.singleShot(900, shot)
app.exec()
