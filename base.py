# File: modules/base.py
# Purpose: Base class for all modules; each module exposes get_widget() and optional on_show(**ctx)

from PySide2.QtWidgets import QWidget

class BaseModule:
    DISPLAY_NAME = "Module"

    def __init__(self, db, parent=None):
        self.db = db
        self.parent = parent
        self.widget = QWidget()

    def get_widget(self) -> QWidget:
        return self.widget

    def on_show(self, **context):
        pass
