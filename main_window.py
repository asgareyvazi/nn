
# =========================================
# file: nikan_drill_master/ui/main_window.py
# =========================================
from __future__ import annotations
from typing import Callable
from PySide6.QtWidgets import QMainWindow, QWidget, QSplitter, QStackedWidget, QFileDialog, QMessageBox
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Qt
from sqlalchemy.orm import Session
from database import session_scope
from ui.styles import DARK, LIGHT
from ui.widgets.ribbon import Ribbon
from ui.widgets.tree_view import HierarchyTree
from modules.base import ModuleBase
from modules import (
    register_modules, MODULES,
)

class MainWindow(QMainWindow):
    def __init__(self, SessionLocal: Callable[[], Session], db_url: str, parent=None):
        super().__init__(parent)
        self.SessionLocal = SessionLocal
        self.db_url = db_url
        self.setWindowTitle("Nikan Drill Master")
        self.resize(1400, 820)

        self.ribbon = Ribbon(self)
        self.stack = QStackedWidget(self)

        with session_scope(self.SessionLocal) as s:
            self.tree = HierarchyTree(s)

        self.tree.tree.itemSelectionChanged.connect(self._on_tree_selection)

        self._modules_by_key: dict[str, ModuleBase] = {}
        self._setup_modules()

        top = QWidget(self)
        top_lay = QVBoxLayout(top)
        top_lay.setContentsMargins(0,0,0,0)
        top_lay.addWidget(self.ribbon)

        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)
        top_lay.addWidget(splitter)

        self.setCentralWidget(top)
        self._apply_theme("dark")

    def _apply_theme(self, theme: str):
        self.setStyleSheet(DARK if theme == "dark" else LIGHT)

    def _setup_modules(self):
        register_modules(self.SessionLocal)
        for key, (title, factory) in MODULES.items():
            mod = factory(self.SessionLocal)
            self._modules_by_key[key] = mod
            self.stack.addWidget(mod)
            self.ribbon.add_action(key, title, callback=lambda _=False, k=key: self._activate_module(k))

    def _activate_module(self, key: str):
        mod = self._modules_by_key[key]
        self.stack.setCurrentWidget(mod)
        mod.on_activated(self._current_selection_payload())

    def _current_selection_payload(self) -> dict:
        item = self.tree.tree.currentItem()
        if not item:
            return {}
        role = item.data(0, Qt.UserRole)
        return {"selection": role}

    def _on_tree_selection(self):
        # sync current module if it relies on selection
        w = self.stack.currentWidget()
        if isinstance(w, ModuleBase):
            w.on_selection_changed(self._current_selection_payload())
