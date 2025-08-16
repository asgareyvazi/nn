# File: ui/widgets/ribbon.py
# Purpose: Simple Ribbon-like horizontal bar with categorized groups and actions.

from PySide2.QtWidgets import QWidget, QHBoxLayout, QToolButton, QMenu
from PySide2.QtCore import Qt

class Ribbon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.l = QHBoxLayout(self)
        self.l.setContentsMargins(6, 6, 6, 6)
        self.l.setSpacing(8)
        self.groups = []

    def add_group(self, title: str, actions: list):
        # actions: list[(text, slot)]
        menu = QMenu(title, self)
        btn = QToolButton(self)
        btn.setText(title)
        btn.setPopupMode(QToolButton.MenuButtonPopup)
        btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        for t, slot in actions:
            act = menu.addAction(t)
            act.triggered.connect(slot)
        btn.setMenu(menu)
        self.l.addWidget(btn)
        self.groups.append(btn)
        return btn
