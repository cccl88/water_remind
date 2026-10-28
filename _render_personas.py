"""渲染三种性格的桌宠对比图（不保存用户配置）"""
import os
import sys
import time

os.environ.setdefault("QT_QPA_PLATFORM", "windows")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter, QColor, QFont

import main as M
from pet.personality import Personality, PERSONALITIES

app = QApplication([])
ctrl = M.Controller(app)
ctrl.config.theme = "light"
ctrl.config.pet_enabled = True
if ctrl.pet is None:
    from pet.pet_window import PetWindow
    ctrl.pet = PetWindow(ctrl)
ctrl.pet.show()

# 先等 Controller 的问候气泡（1.4s 定时器）弹完，避免覆盖正式渲染
t0 = time.time()
while time.time() - t0 < 1.8:
    app.processEvents()
    time.sleep(0.05)
ctrl.pet.close_bubble()

cells = []
for key in ("tsundere", "gentle", "coquettish"):
    ctrl.persona = Personality(key)
    ctrl.pet.remind(ctrl.persona.say("remind"))
    t0 = time.time()
    while time.time() - t0 < 1.1:
        app.processEvents()
        time.sleep(0.05)
    pm_pet = ctrl.pet.grab()
    pm_bub = ctrl.pet.bubble.grab() if ctrl.pet.bubble is not None else None
    cells.append((key, PERSONALITIES[key]["name"], pm_pet, pm_bub))
    ctrl.pet.close_bubble()

cw = 280
ch = 250 + 150 + 50
img = QImage(cw * 3, ch, QImage.Format_ARGB32)
img.fill(QColor("#EAF1FA"))
qp = QPainter(img)
qp.setRenderHint(QPainter.Antialiasing)
for i, (key, name, pm_pet, pm_bub) in enumerate(cells):
    x0 = i * cw
    if pm_bub:
        qp.drawPixmap(x0 + (cw - pm_bub.width()) // 2, 20, pm_bub)
    qp.drawPixmap(x0 + (cw - pm_pet.width()) // 2, 20 + 150, pm_pet)
    qp.setPen(QColor("#334155"))
    qp.setFont(QFont("Microsoft YaHei UI", 13, QFont.Bold))
    qp.drawText(x0, ch - 26, cw, 24, 0x84, name)  # AlignHCenter|AlignVCenter
qp.end()

img.save("assets/personas.png")
print("rendered 3 personas")
