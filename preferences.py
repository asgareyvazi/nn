# File: modules/preferences.py
# Purpose: App preferences: units, theme, load previous report, logos path.

from PySide2.QtWidgets import QWidget, QFormLayout, QComboBox, QCheckBox, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from .base import BaseModule
from models import Preferences

class PreferencesWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load()

    def _build(self):
        self.l = QVBoxLayout(self)
        frm = QFormLayout()
        self.cb_units = QComboBox(); self.cb_units.addItems(["metric","imperial"])
        self.cb_theme = QComboBox(); self.cb_theme.addItems(["dark","light"])
        self.chk_load_prev = QCheckBox("Load Previous Report")
        self.btn_logo_company = QPushButton("Upload Company Logo"); self.btn_logo_client = QPushButton("Upload Client Logo")
        self.btn_save = QPushButton("Save Preferences")
        frm.addRow("Default Units", self.cb_units); frm.addRow("Theme", self.cb_theme); frm.addRow(self.chk_load_prev)
        frm.addRow("Company Logo", self.btn_logo_company); frm.addRow("Client Logo", self.btn_logo_client)
        self.l.addLayout(frm); self.l.addWidget(self.btn_save)
        self.btn_logo_company.clicked.connect(lambda: self._pick("company"))
        self.btn_logo_client.clicked.connect(lambda: self._pick("client"))
        self.btn_save.clicked.connect(self._save)
        self._logo_paths = {"company": None, "client": None}

    def _load(self):
        with self.db.get_session() as s:
            pref = s.query(Preferences).first()
            if not pref:
                pref = Preferences(default_units="metric", load_previous_report=True, theme="dark"); s.add(pref); s.flush()
            self.cb_units.setCurrentText(pref.default_units or "metric")
            self.cb_theme.setCurrentText(pref.theme or "dark")
            self.chk_load_prev.setChecked(bool(pref.load_previous_report))
            self._logo_paths["company"] = pref.logo_company
            self._logo_paths["client"] = pref.logo_client

    def _pick(self, which):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.svg)")
        if fname:
            self._logo_paths[which] = fname
            QMessageBox.information(self, "Picked", f"Picked {which} logo: {fname}")

    def _save(self):
        with self.db.get_session() as s:
            pref = s.query(Preferences).first()
            if not pref:
                pref = Preferences(); s.add(pref)
            pref.default_units = self.cb_units.currentText()
            pref.theme = self.cb_theme.currentText()
            pref.load_previous_report = self.chk_load_prev.isChecked()
            pref.logo_company = self._logo_paths.get("company")
            pref.logo_client = self._logo_paths.get("client")
        QMessageBox.information(self, "Saved", "Preferences saved.")

class PreferencesModule(BaseModule):
    DISPLAY_NAME = "Preferences"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = PreferencesWidget(self.db)
    def get_widget(self): return self.widget
