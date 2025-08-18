
# =========================================
# file: nikan_drill_master/modules/base.py
# =========================================
from __future__ import annotations
from typing import Callable
from PySide6.QtWidgets import QWidget
from sqlalchemy.orm import Session

class ModuleBase(QWidget):
    """چرا: الگوی مشترک برای همه ماژول‌ها (چرخه‌ی حیات و Session)"""
    def __init__(self, SessionLocal: Callable[[], Session], parent=None):
        super().__init__(parent)
        self.SessionLocal = SessionLocal

    # Hooks
    def on_activated(self, context: dict) -> None:
        pass

    def on_selection_changed(self, context: dict) -> None:
        pass
