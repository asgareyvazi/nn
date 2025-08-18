
# =========================================
# file: nikan_drill_master/modules/preferences.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QComboBox, QCheckBox, QPushButton, QFileDialog, QLabel
from modules.base import ModuleBase
from database import session_scope
from sqlalchemy.orm import Session
from models import Preferences

class PreferencesModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.units = QComboBox(); self.units.addItems(["", "SI", "Field"])
        self.load_prev = QCheckBox("Load Previous Report")
        self.theme = QComboBox(); self.theme.addItems(["", "dark", "light"])
        self.logo_path = QLabel("No logo selected")
        pick = QPushButton("Choose Logo")
        pick.clicked.connect(self._choose_logo)
        save = QPushButton("Save")
        save.clicked.connect(self._save)
        form.addRow("Default Units", self.units)
        form.addRow("", self.load_prev)
        form.addRow("Theme", self.theme)
        form.addRow("Company Logo", pick)
        lay.addLayout(form); lay.addWidget(self.logo_path); lay.addWidget(save)

    def _choose_logo(self):
        p, _ = QFileDialog.getOpenFileName(self, "Choose Logo", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if p:
            self.logo_path.setText(p)

    def _load(self):
        with session_scope(self.SessionLocal) as s:
            pref = s.query(Preferences).first()
            if pref:
                self.units.setCurrentText(pref.default_units or "")
                self.load_prev.setChecked(bool(pref.load_previous_report))
                self.theme.setCurrentText(pref.theme or "")
                if pref.logo_path:
                    self.logo_path.setText(pref.logo_path)

    def _save(self):
        with session_scope(self.SessionLocal) as s:
            pref = s.query(Preferences).first()
            if not pref:
                pref = Preferences()
                s.add(pref)
            pref.default_units = self.units.currentText() or None
            pref.load_previous_report = self.load_prev.isChecked()
            pref.theme = self.theme.currentText() or None
            p = self.logo_path.text()
            pref.logo_path = p if p and p != "No logo selected" else None
