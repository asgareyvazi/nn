# File: modules/weather_data.py
# Purpose: Weather metrics per section.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox, QLineEdit, QPushButton, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, Weather

class WeatherWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        frm = QFormLayout()
        self.wind = QDoubleSpinBox(); self.direction = QLineEdit(); self.temp = QDoubleSpinBox(); self.vis = QDoubleSpinBox()
        for w in (self.wind, self.temp, self.vis): w.setRange(-1000,1e6); w.setDecimals(2)
        frm.addRow("Wind Speed", self.wind); frm.addRow("Direction", self.direction); frm.addRow("Temperature", self.temp); frm.addRow("Visibility", self.vis)
        self.l.addLayout(frm)
        btn = QPushButton("Save"); btn.clicked.connect(self._save); self.l.addWidget(btn)
        self.cb_section.currentIndexChanged.connect(self._load)
        self._load_sections()

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _load(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            rec = s.query(Weather).filter_by(section_id=sid).first()
        if not rec:
            self.wind.setValue(0); self.direction.setText(""); self.temp.setValue(0); self.vis.setValue(0); return
        self.wind.setValue(rec.wind_speed or 0); self.direction.setText(rec.direction or ""); self.temp.setValue(rec.temperature or 0); self.vis.setValue(rec.visibility or 0)

    def _save(self):
        sid = self.cb_section.currentData(); 
        if sid is None: return
        with self.db.get_session() as s:
            rec = s.query(Weather).filter_by(section_id=sid).first()
            if not rec: rec = Weather(section_id=sid); s.add(rec)
            rec.wind_speed = self.wind.value(); rec.direction = self.direction.text().strip(); rec.temperature = self.temp.value(); rec.visibility = self.vis.value()
        QMessageBox.information(self, "Saved", "Weather data saved.")

class WeatherModule(BaseModule):
    DISPLAY_NAME = "Weather Data"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = WeatherWidget(self.db)
    def get_widget(self): return self.widget
