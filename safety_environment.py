# File: modules/safety_environment.py
# Purpose: Safety & BOP records, drills log and basic BOP test records CRUD.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PySide2.QtCore import QDate
from .base import BaseModule
from models import Section, BOPRecord
from datetime import date

class SafetyEnvironmentWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build()
        self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QLineEdit()  # replaced with simple input for performance; caller can type "section_id"
        self.l.addWidget(self.cb_section)

        frm = QFormLayout()
        self.dt_fire = QDateEdit(); self.dt_fire.setCalendarPopup(True); self.dt_bop = QDateEdit(); self.dt_bop.setCalendarPopup(True)
        self.dt_h2s = QDateEdit(); self.dt_h2s.setCalendarPopup(True)
        self.le_days_no_lti = QLineEdit(); self.le_days_no_lta = QLineEdit()
        self.le_rams = QLineEdit(); self.le_pressure_test = QLineEdit(); self.le_koomey = QLineEdit()
        self.le_bop_stack = QLineEdit(); self.le_bop_type = QLineEdit(); self.le_wp = QLineEdit(); self.le_size = QLineEdit()

        for w in (self.dt_fire, self.dt_bop, self.dt_h2s):
            w.setDate(QDate.currentDate())

        frm.addRow("Last Fire Drill", self.dt_fire)
        frm.addRow("Last BOP Drill", self.dt_bop)
        frm.addRow("Last H2S Drill", self.dt_h2s)
        frm.addRow("Days w/o LTI", self.le_days_no_lti)
        frm.addRow("Days w/o LTA", self.le_days_no_lta)
        frm.addRow("Rams / Pressure / Koomey", self.le_rams)
        frm.addRow("Pressure Test", self.le_pressure_test)
        frm.addRow("Koomey Test", self.le_koomey)
        frm.addRow("BOP Stack (Name / Type / WP / Size)", self.le_bop_stack)

        self.l.addLayout(frm)
        btns = QVBoxLayout()
        self.btn_load = QPushButton("Load By Section ID"); self.btn_save = QPushButton("Save")
        self.btn_load.clicked.connect(self._load)
        self.btn_save.clicked.connect(self._save)
        btns.addWidget(self.btn_load); btns.addWidget(self.btn_save)
        self.l.addLayout(btns)

    def _load_sections(self):
        # nothing fancy: user types section id
        pass

    def _load(self):
        try:
            sid = int(self.cb_section.text().strip())
        except Exception:
            QMessageBox.warning(self, "Input", "Enter numeric section id in the field above")
            return
        with self.db.get_session() as s:
            rec = s.query(BOPRecord).filter_by(section_id=sid).first()
        if not rec:
            QMessageBox.information(self, "Not found", "No record found for this section; you can save new.")
            return
        if rec.last_fire: self.dt_fire.setDate(QDate(rec.last_fire.year, rec.last_fire.month, rec.last_fire.day))
        if rec.last_bop: self.dt_bop.setDate(QDate(rec.last_bop.year, rec.last_bop.month, rec.last_bop.day))
        if rec.last_h2s: self.dt_h2s.setDate(QDate(rec.last_h2s.year, rec.last_h2s.month, rec.last_h2s.day))
        self.le_days_no_lti.setText(str(rec.days_without_lti or ""))
        self.le_days_no_lta.setText(str(rec.days_without_lta or ""))
        self.le_rams.setText(rec.rams or ""); self.le_pressure_test.setText(rec.pressure_test or ""); self.le_koomey.setText(rec.koomey_test or "")
        self.le_bop_stack.setText(f"{rec.bop_stack_name} | {rec.bop_type} | {rec.wp} | {rec.size}")

    def _save(self):
        try:
            sid = int(self.cb_section.text().strip())
        except Exception:
            QMessageBox.warning(self, "Input", "Enter numeric section id in the field above")
            return
        with self.db.get_session() as s:
            rec = s.query(BOPRecord).filter_by(section_id=sid).first()
            if not rec:
                rec = BOPRecord(section_id=sid); s.add(rec)
            rec.last_fire = self.dt_fire.date().toPython()
            rec.last_bop = self.dt_bop.date().toPython()
            rec.last_h2s = self.dt_h2s.date().toPython()
            try:
                rec.days_without_lti = int(self.le_days_no_lti.text()) if self.le_days_no_lti.text() else None
            except:
                rec.days_without_lti = None
            try:
                rec.days_without_lta = int(self.le_days_no_lta.text()) if self.le_days_no_lta.text() else None
            except:
                rec.days_without_lta = None
            rec.rams = self.le_rams.text().strip(); rec.pressure_test = self.le_pressure_test.text().strip(); rec.koomey_test = self.le_koomey.text().strip()
            # parse bop_stack simple
            rec.bop_stack_name = self.le_bop_stack.text().strip()
        QMessageBox.information(self, "Saved", "Safety/BOP record saved.")

class SafetyEnvironmentModule(BaseModule):
    DISPLAY_NAME = "Safety & BOP"
    def __init__(self, db, parent=None):
        super().__init__(db, parent)
        self.widget = SafetyEnvironmentWidget(self.db)
    def get_widget(self): return self.widget
