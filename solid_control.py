# File: modules/solid_control.py
# Purpose: Solid control unit metrics.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, SolidControlUnit

class SolidControlWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        frm = QFormLayout()
        self.le_equip = QLineEdit = None
        self.equipment = QLineEdit = None
        self.equipment = QPushButton("Placeholder")  # to keep simple
        self.feed = QDoubleSpinBox(); self.hours = QDoubleSpinBox(); self.loss = QDoubleSpinBox()
        self.size_cones = QLineEdit = None
        self.uf = QLineEdit = None
        self.of = QLineEdit = None
        self.daily_hours = QDoubleSpinBox(); self.cum_hours = QDoubleSpinBox()
        for w in (self.feed, self.hours, self.loss, self.daily_hours, self.cum_hours):
            w.setRange(0, 1e6); w.setDecimals(2)
        # simple fields
        frm.addRow("Feed (bbl/hr)", self.feed); frm.addRow("Hours", self.hours); frm.addRow("Loss (bbl)", self.loss)
        frm.addRow("Daily Hrs / Cum Hrs", self._pair(self.daily_hours, self.cum_hours))
        self.l.addLayout(frm)
        btn = QPushButton("Save"); btn.clicked.connect(self._save); self.l.addWidget(btn)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _pair(self, a,b):
        from PySide2.QtWidgets import QWidget, QHBoxLayout
        w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(0,0,0,0); l.addWidget(a); l.addWidget(b); return w

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _load(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            rec = s.query(SolidControlUnit).filter_by(section_id=sid).first()
        if not rec:
            for w in (self.feed, self.hours, self.loss, self.daily_hours, self.cum_hours): w.setValue(0)
            return
        self.feed.setValue(rec.feed_bbl_hr or 0); self.hours.setValue(rec.hours or 0); self.loss.setValue(rec.loss_bbl or 0)
        self.daily_hours.setValue(rec.daily_hours or 0); self.cum_hours.setValue(rec.cum_hours or 0)

    def _save(self):
        sid = self.cb_section.currentData(); 
        if sid is None: return
        with self.db.get_session() as s:
            rec = s.query(SolidControlUnit).filter_by(section_id=sid).first()
            if not rec: rec = SolidControlUnit(section_id=sid); s.add(rec)
            rec.equipment = ""  # placeholder
            rec.feed_bbl_hr = self.feed.value(); rec.hours = self.hours.value(); rec.loss_bbl = self.loss.value()
            rec.daily_hours = self.daily_hours.value(); rec.cum_hours = self.cum_hours.value()
        QMessageBox.information(self, "Saved", "Solid control data saved.")

class SolidControlModule(BaseModule):
    DISPLAY_NAME = "Solid Control"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = SolidControlWidget(self.db)
    def get_widget(self): return self.widget
