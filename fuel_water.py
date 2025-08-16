# File: modules/fuel_water.py
# Purpose: Fuel & water daily consumption + bulk stock editor.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, FuelWater, BulkStock

class FuelWaterWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        frm = QFormLayout()
        self.desc = QLineEdit = None
        self.consumed = QDoubleSpinBox(); self.stock = QDoubleSpinBox(); self.unit = QLineEdit = None
        self.consumed.setRange(0,1e6); self.stock.setRange(0,1e6); self.consumed.setDecimals(2); self.stock.setDecimals(2)
        frm.addRow("Consumed", self.consumed); frm.addRow("Stock", self.stock)
        self.l.addLayout(frm)
        btn = QPushButton("Save"); btn.clicked.connect(self._save); self.l.addWidget(btn)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _load(self):
        sid = self.cb_section.currentData(); 
        if sid is None: return
        with self.db.get_session() as s:
            rec = s.query(FuelWater).filter_by(section_id=sid).first()
        if not rec:
            self.consumed.setValue(0); self.stock.setValue(0); return
        self.consumed.setValue(rec.consumed or 0); self.stock.setValue(rec.stock or 0)

    def _save(self):
        sid = self.cb_section.currentData(); 
        if sid is None: return
        with self.db.get_session() as s:
            rec = s.query(FuelWater).filter_by(section_id=sid).first()
            if not rec: rec = FuelWater(section_id=sid); s.add(rec)
            rec.consumed = self.consumed.value(); rec.stock = self.stock.value()
        QMessageBox.information(self, "Saved", "Fuel & Water saved.")

class FuelWaterModule(BaseModule):
    DISPLAY_NAME = "Fuel & Water"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = FuelWaterWidget(self.db)
    def get_widget(self): return self.widget
