"""渲染桌宠+气泡合成图（检查整体效果）"""
import os
import sys
import time

os.environ.setdefault("QT_QPA_PLATFORM", "windows")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter, QColor

import main as M

app = QApplication([])
ctrl = M.Controller(app)

ctrl.config.theme = "light"  # 仅本次渲染用浅色检查
ctrl.config.pet_enabled = True
if ctrl.pet is None:
    from pet.pet_window import PetWindow
    ctrl.pet = PetWindow(ctrl)
ctrl.pet.show()
# 先等问候气泡（1.4s 定时器）弹完再渲染，避免被覆盖
t0 = time.time()
while time.time() - t0 < 1.8:
    app.processEvents()
    time.sleep(0.05)
ctrl.pet.close_bubble()
ctrl.pet.remind(ctrl.persona.say("remind"))

t0 = time.time()
while time.time() - t0 < 1.3:
    app.processEvents()
    time.sleep(0.05)

pm_pet = ctrl.pet.grab()
pm_bub = ctrl.pet.bubble.grab() if ctrl.pet.bubble is not None else None

w = max(pm_pet.width(), pm_bub.width() if pm_bub else 0) + 60
h = pm_pet.height() + (pm_bub.height() if pm_bub else 0) + 30
img = QImage(w, h, QImage.Format_ARGB32)
img.fill(QColor("#EAF1FA"))
qp = QPainter(img)
if pm_bub:
    qp.drawPixmap((w - pm_bub.width()) // 2, 0, pm_bub)
qp.drawPixmap((w - pm_pet.width()) // 2, (pm_bub.height() if pm_bub else 0) + 10, pm_pet)
qp.end()

os.makedirs("assets", exist_ok=True)
img.save("assets/pet_preview.png")
print("pet rendered:", ctrl.persona.name, "| bubble:", pm_bub is not None)
