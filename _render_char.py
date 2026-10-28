"""角色渲染预览：把各表情画在一张网格图里，便于调整外观"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtGui import QColor, QPainter, QFont, QImage, QPixmap
from PySide6.QtWidgets import QApplication

from pet.character import Character

app = QApplication([])

exprs = ["idle", "happy", "shy", "angry", "surprised", "sleepy"]
cw, ch = 200, 250
cols = 3
rows = (len(exprs) + cols - 1) // cols
img = QImage(cw * cols, ch * rows + 40, QImage.Format_ARGB32)
img.fill(QColor("#F2F6FC"))

p = QPainter(img)
p.setRenderHint(QPainter.Antialiasing)
c = Character()
for i, e in enumerate(exprs):
    col, row = i % cols, i // cols
    x, y = col * cw, row * ch + 40
    p.save()
    p.translate(x, y)
    c.paint(p, cw, ch, expr=e, t=0.0, blink=(e == "sleepy"))
    p.restore()
    p.setPen(QColor("#334155"))
    p.setFont(QFont("Microsoft YaHei UI", 11))
    p.drawText(x + 12, y - 10, e)

# 大图单张
big = QImage(320, 400, QImage.Format_ARGB32)
big.fill(QColor("#F2F6FC"))
p2 = QPainter(big)
p2.setRenderHint(QPainter.Antialiasing)
c.paint(p2, 320, 400, expr="idle", t=0.0)
p2.end()

p.end()
os.makedirs("assets", exist_ok=True)
img.save("assets/_char_grid.png")
big.save("assets/_char_big.png")
print("rendered")
