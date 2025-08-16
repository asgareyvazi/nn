# File: ui/styles.py
# Purpose: Central app palette and fonts (dark/light), industrial vibe similar to Petrel/Landmark.

from PySide2.QtGui import QPalette, QColor, QFont
from PySide2.QtWidgets import QApplication

def load_app_palette(app: QApplication, theme="dark"):
    pal = QPalette()
    if theme == "dark":
        base = QColor(30, 32, 36)
        window = QColor(24, 26, 30)
        text = QColor(230, 232, 235)
        hl = QColor(70, 130, 180)
        pal.setColor(QPalette.Window, window)
        pal.setColor(QPalette.WindowText, text)
        pal.setColor(QPalette.Base, base)
        pal.setColor(QPalette.AlternateBase, QColor(38, 40, 45))
        pal.setColor(QPalette.Text, text)
        pal.setColor(QPalette.Button, QColor(45, 47, 52))
        pal.setColor(QPalette.ButtonText, text)
        pal.setColor(QPalette.Highlight, hl)
        pal.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    else:
        pal = app.palette()  # system theme
    app.setPalette(pal)

def apply_font_defaults(app: QApplication):
    f = QFont("Segoe UI", 9)
    app.setFont(f)
