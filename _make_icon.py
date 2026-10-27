"""生成应用图标 app.ico（与界面水滴风格一致）"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
from PySide6.QtWidgets import QApplication

from ui.widgets import water_drop_pixmap

app = QApplication([])

tmp = "_icon_src.png"
pm = water_drop_pixmap(512, "#2E90FF")
pm.save(tmp, "PNG")

img = Image.open(tmp).convert("RGBA")
img.save(
    "app.ico",
    format="ICO",
    sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
)
os.remove(tmp)
print("icon ->", os.path.abspath("app.ico"))
