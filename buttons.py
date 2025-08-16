# File: ui/widgets/buttons.py
# Purpose: Common button factory helpers & icons

from PySide2.QtWidgets import QPushButton
from PySide2.QtGui import QIcon

def icon_button(text: str, icon_path: str = None):
    b = QPushButton(text)
    if icon_path:
        b.setIcon(QIcon(icon_path))
    b.setMinimumHeight(28)
    return b
