# File: modules/drilling_parameters.py
# Purpose: Editor for Drilling Parameters per Section (min/max + SCR pumps).

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, DrillingParameters

class DrillingParametersWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        v = QVBoxLayout(self)
        self.cb_section = QComboBox(); v.addWidget(self.cb_section)
        frm = QFormLayout(); v.addLayout(frm)

        self.wob_min=QDoubleSpinBox(); self.wob_max=QDoubleSpinBox()
        self.rpm_s_min=QDoubleSpinBox(); self.rpm_s_max=QDoubleSpinBox()
        self.rpm_m_min=QDoubleSpinBox(); self.rpm_m_max=QDoubleSpinBox()
        self.tq_min=QDoubleSpinBox(); self.tq_max=QDoubleSpinBox()
        self.pp_min=QDoubleSpinBox(); self.pp_max=QDoubleSpinBox()
        self.po_min=QDoubleSpinBox(); self.po_max=QDoubleSpinBox()
        self.hsi=QDoubleSpinBox(); self.av=QDoubleSpinBox(); self.tfa=QDoubleSpinBox(); self.rev=QDoubleSpinBox()
        self.scr1_spm=QDoubleSpinBox(); self.scr1_spp=QDoubleSpinBox()
        self.scr2_spm=QDoubleSpinBox(); self.scr2_spp=QDoubleSpinBox()
        self.scr3_spm=QDoubleSpinBox(); self.scr3_spp=QDoubleSpinBox()

        for w in [self.wob_min,self.wob_max,self.rpm_s_min,self.rpm_s_max,self.rpm_m_min,self.rpm_m_max,
                  self.tq_min,self.tq_max,self.pp_min,self.pp_max,self.po_min,self.po_max,
                  self.hsi,self.av,self.tfa,self.rev,self.scr1_spm,self.scr1_spp,self.scr2_spm,self.scr2_spp,self.scr3_spm,self.scr3_spp]:
            w.setRange(0, 1e6); w.setDecimals(2)

        frm.addRow("WOB min/max", self._pair(self.wob_min, self.wob_max))
        frm.addRow("Surface RPM min/max", self._pair(self.rpm_s_min, self.rpm_s_max))
        frm.addRow("Motor RPM min/max", self._pair(self.rpm_m_min, self.rpm_m_max))
        frm.addRow("Torque min/max", self._pair(self.tq_min, self.tq_max))
        frm.addRow("Pump Pressure min/max", self._pair(self.pp_min, self.pp_max))
        frm.addRow("Pump Output min/max", self._pair(self.po_min, self.po_max))
        frm.addRow("HSI / Annular Velocity / TFA / Revolution", self._quad(self.hsi, self.av, self.tfa, self.rev))
        frm.addRow("SCR#1 SPM/SPP", self._pair(self.scr1_spm, self.scr1_spp))
        frm.addRow("SCR#2 SPM/SPP", self._pair(self.scr2_spm, self.scr2_spp))
        frm.addRow("SCR#3 SPM/SPP", self._pair(self.scr3_spm, self.scr3_spp))

        btn = QPushButton("Save"); btn.clicked.connect(self._save); v.addWidget(btn)

        self.cb_section.currentIndexChanged.connect(self._load_for_section)

    def _pair(self, a, b):
        from PySide2.QtWidgets import QWidget, QHBoxLayout
        w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(0,0,0,0); l.addWidget(a); l.addWidget(b); return w

    def _quad(self, a,b,c,d):
        from PySide2.QtWidgets import QWidget, QHBoxLayout
        w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(0,0,0,0); [l.addWidget(x) for x in (a,b,c,d)]; return w

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).order_by(Section.id.desc()).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)
        self._load_for_section()

    def _load_for_section(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            d = s.query(DrillingParameters).filter_by(section_id=sid).first()
        if not d:
            for w in (self.wob_min,self.wob_max,self.rpm_s_min,self.rpm_s_max,self.rpm_m_min,self.rpm_m_max,self.tq_min,self.tq_max,
                      self.pp_min,self.pp_max,self.po_min,self.po_max,self.hsi,self.av,self.tfa,self.rev,
                      self.scr1_spm,self.scr1_spp,self.scr2_spm,self.scr2_spp,self.scr3_spm,self.scr3_spp): w.setValue(0)
        else:
            self.wob_min.setValue(d.wob_min or 0); self.wob_max.setValue(d.wob_max or 0)
            self.rpm_s_min.setValue(d.rpm_surface_min or 0); self.rpm_s_max.setValue(d.rpm_surface_max or 0)
            self.rpm_m_min.setValue(d.rpm_motor_min or 0); self.rpm_m_max.setValue(d.rpm_motor_max or 0)
            self.tq_min.setValue(d.torque_min or 0); self.tq_max.setValue(d.torque_max or 0)
            self.pp_min.setValue(d.pump_pressure_min or 0); self.pp_max.setValue(d.pump_pressure_max or 0)
            self.po_min.setValue(d.pump_output_min or 0); self.po_max.setValue(d.pump_output_max or 0)
            self.hsi.setValue(d.hsi or 0); self.av.setValue(d.annular_velocity or 0); self.tfa.setValue(d.tfa or 0); self.rev.setValue(d.bit_revolution or 0)
            self.scr1_spm.setValue(d.scr1_spm or 0); self.scr1_spp.setValue(d.scr1_spp or 0)
            self.scr2_spm.setValue(d.scr2_spm or 0); self.scr2_spp.setValue(d.scr2_spp or 0)
            self.scr3_spm.setValue(d.scr3_spm or 0); self.scr3_spp.setValue(d.scr3_spp or 0)

    def _save(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            d = s.query(DrillingParameters).filter_by(section_id=sid).first()
            if not d:
                d = DrillingParameters(section_id=sid); s.add(d)
            d.wob_min=self.wob_min.value(); d.wob_max=self.wob_max.value()
            d.rpm_surface_min=self.rpm_s_min.value(); d.rpm_surface_max=self.rpm_s_max.value()
            d.rpm_motor_min=self.rpm_m_min.value(); d.rpm_motor_max=self.rpm_m_max.value()
            d.torque_min=self.tq_min.value(); d.torque_max=self.tq_max.value()
            d.pump_pressure_min=self.pp_min.value(); d.pump_pressure_max=self.pp_max.value()
            d.pump_output_min=self.po_min.value(); d.pump_output_max=self.po_max.value()
            d.hsi=self.hsi.value(); d.annular_velocity=self.av.value(); d.tfa=self.tfa.value(); d.bit_revolution=self.rev.value()
            d.scr1_spm=self.scr1_spm.value(); d.scr1_spp=self.scr1_spp.value()
            d.scr2_spm=self.scr2_spm.value(); d.scr2_spp=self.scr2_spp.value()
            d.scr3_spm=self.scr3_spm.value(); d.scr3_spp=self.scr3_spp.value()
        QMessageBox.information(self, "Saved", "Drilling parameters saved.")

class DrillingParametersModule(BaseModule):
    DISPLAY_NAME = "Drilling Parameters"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = DrillingParametersWidget(self.db)
    def get_widget(self): return self.widget
