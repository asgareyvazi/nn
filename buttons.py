# =========================================
# file: nikan_drill_master/ui/widgets/buttons.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QPushButton

class PrimaryButton(QPushButton):
    pass

class DangerButton(QPushButton):
    pass

# =========================================
# file: nikan_drill_master/ui/widgets/ribbon.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QHBoxLayout, QToolButton, QMenu
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

class Ribbon(QWidget):
    """چرا: ناوبری سریع ماژول‌ها با حس صنعتی مشابه Petrel/Landmark"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons: dict[str, QToolButton] = {}
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 6, 8, 6)
        self._layout.setSpacing(8)

    def add_action(self, key: str, text: str, icon: QIcon | None = None, menu: QMenu | None = None, callback=None):
        btn = QToolButton(self)
        btn.setText(text)
        btn.setToolButtonStyle(btn.ToolButtonTextUnderIcon)
        btn.setIcon(icon or QIcon())
        btn.setIconSize(QSize(24, 24))
        if menu:
            btn.setMenu(menu)
            btn.setPopupMode(QToolButton.MenuButtonPopup)
        if callback:
            btn.clicked.connect(callback)
        self._layout.addWidget(btn)
        self._buttons[key] = btn
