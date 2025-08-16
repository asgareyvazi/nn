# File: modules/waste_management.py
# Purpose: Waste metrics per section CRUD.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, WasteManagement

class WasteManagementWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build()
        self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        frm = QFormLayout()
        self.recycled = QDoubleSpinBox(); self.ph = QDoubleSpinBox(); self.turbidity = QDoubleSpinBox()
        self.hardness = QDoubleSpinBox(); self.cutting_trans = QDoubleSpinBox()
        for w in (self.recycled, self.ph, self.turbidity, self.hardness, self.cutting_trans):
            w.setRange(0, 1e6); w.setDecimals(3)
        frm.addRow("Recycled (BBL)", self.recycled); frm.addRow("pH", self.ph); frm.addRow("Turbidity/TSS", self.turbidity)
        frm.addRow("Hardness / Ca++", self.hardness); frm.addRow("Cuttings Transport (m3)", self.cutting_trans)
        self.l.addLayout(frm)
        btn = QPushButton("Save"); btn.clicked.connect(self._save); self.l.addWidget(btn)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _load(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            rec = s.query(WasteManagement).filter_by(section_id=sid).first()
        if not rec:
            for w in (self.recycled, self.ph, self.turbidity, self.hardness, self.cutting_trans): w.setValue(0)
            return
        self.recycled.setValue(rec.recycled_bbl or 0); self.ph.setValue(rec.ph or 0); self.turbidity.setValue(rec.turbidity_tss or 0)
        self.hardness.setValue(rec.hardness_ca or 0); self.cutting_trans.setValue(rec.cutting_trans_m3 or 0)

    def _save(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            rec = s.query(WasteManagement).filter_by(section_id=sid).first()
            if not rec: rec = WasteManagement(section_id=sid); s.add(rec)
            rec.recycled_bbl = self.recycled.value(); rec.ph = self.ph.value(); rec.turbidity_tss = self.turbidity.value()
            rec.hardness_ca = self.hardness.value(); rec.cutting_trans_m3 = self.cutting_trans.value()
        QMessageBox.information(self, "Saved", "Waste management saved.")

class WasteManagementModule(BaseModule):
    DISPLAY_NAME = "Waste Management"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = WasteManagementWidget(self.db)
    def get_widget(self): return self.widget
