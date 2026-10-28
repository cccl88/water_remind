"""滚动主窗口到「桌宠」设置区并截图"""
import os
import sys
import time

os.environ.setdefault("QT_QPA_PLATFORM", "windows")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QScrollArea

import main as M

app = QApplication([])
ctrl = M.Controller(app)
ctrl.config.theme = "light"
ctrl.apply_theme("light")
win = ctrl.window
win.show()

t0 = time.time()
while time.time() - t0 < 1.0:
    app.processEvents()
    time.sleep(0.05)

scroll = win.findChild(QScrollArea)
scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum() - 100)

t0 = time.time()
while time.time() - t0 < 0.6:
    app.processEvents()
    time.sleep(0.05)

win.grab().save("assets/preview_settings_pet.png")
print("settings shot ok")
