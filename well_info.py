# File: modules/well_info.py
# Purpose: Full Well Info editor (create/edit Company, Project, Well, Section) with hierarchy controls.

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox, QGroupBox, QDateEdit
)
from PySide2.QtCore import QDate
from .base import BaseModule
from models import Company, Project, Well, Section
from datetime import date

class WellInfoWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db
        self._build(); self._load_companies()

    def _build(self):
        root = QVBoxLayout(self)

        # Company / Project selectors
        sel_box = QGroupBox("Company / Project / Well / Section")
        sel_l = QHBoxLayout(sel_box)
        self.cb_company = QComboBox(); self.cb_project = QComboBox(); self.cb_well = QComboBox(); self.cb_section = QComboBox()
        for w in (self.cb_company, self.cb_project, self.cb_well, self.cb_section): sel_l.addWidget(w)
        self.cb_company.currentIndexChanged.connect(self._on_company_changed)
        self.cb_project.currentIndexChanged.connect(self._on_project_changed)
        self.cb_well.currentIndexChanged.connect(self._on_well_changed)
        root.addWidget(sel_box)

        # Add buttons
        btns = QHBoxLayout()
        self.btn_add_company = QPushButton("Add Company"); self.btn_add_project=QPushButton("Add Project")
        self.btn_add_well=QPushButton("Add Well"); self.btn_add_section=QPushButton("Add Section")
        for b in (self.btn_add_company, self.btn_add_project, self.btn_add_well, self.btn_add_section): btns.addWidget(b)
        root.addLayout(btns)
        self.btn_add_company.clicked.connect(self._add_company)
        self.btn_add_project.clicked.connect(self._add_project)
        self.btn_add_well.clicked.connect(self._add_well)
        self.btn_add_section.clicked.connect(self._add_section)

        # Well form
        self.frm = QFormLayout()
        self.le_well_name = QLineEdit(); self.le_rig_name = QLineEdit(); self.le_operator = QLineEdit(); self.le_field = QLineEdit()
        self.cb_well_type = QComboBox(); self.cb_well_type.addItems(["Onshore","Offshore"])
        self.cb_rig_type = QComboBox(); self.cb_rig_type.addItems(["Land","Jackup","SemiSub","Others"])
        self.cb_shape = QComboBox(); self.cb_shape.addItems(["Vertical","Deviated","Horizontal"])

        self.sp_derrick = QSpinBox(); self.sp_derrick.setRange(0, 100000)

        self.sp_gle = QDoubleSpinBox(); self.sp_gle.setDecimals(2); self.sp_gle.setRange(-10000, 10000)
        self.sp_rte = QDoubleSpinBox(); self.sp_rte.setDecimals(2); self.sp_rte.setRange(-10000, 10000)
        self.sp_msl = QDoubleSpinBox(); self.sp_msl.setDecimals(2); self.sp_msl.setRange(-10000, 10000)
        self.sp_kop1 = QDoubleSpinBox(); self.sp_kop2 = QDoubleSpinBox()

        self.le_lat = QLineEdit(); self.le_lon = QLineEdit(); self.le_northing = QLineEdit(); self.le_easting = QLineEdit()

        self.sp_hole_in = QDoubleSpinBox(); self.sp_hole_in.setRange(0, 60); self.sp_final_md = QDoubleSpinBox(); self.sp_final_md.setRange(0, 50000)
        self.sp_wd = QDoubleSpinBox(); self.sp_wd.setRange(0, 5000)

        self.dt_spud = QDateEdit(); self.dt_spud.setCalendarPopup(True)
        self.dt_start_hole = QDateEdit(); self.dt_start_hole.setCalendarPopup(True)
        self.dt_rig_move = QDateEdit(); self.dt_rig_move.setCalendarPopup(True)
        for d in (self.dt_spud, self.dt_start_hole, self.dt_rig_move): d.setDate(QDate.currentDate())

        self.frm.addRow("Well Name", self.le_well_name)
        self.frm.addRow("Rig Name", self.le_rig_name)
        self.frm.addRow("Operator", self.le_operator)
        self.frm.addRow("Field", self.le_field)
        self.frm.addRow("Well Type", self.cb_well_type)
        self.frm.addRow("Rig Type", self.cb_rig_type)
        self.frm.addRow("Well Shape", self.cb_shape)
        self.frm.addRow("Derrick Height (ft)", self.sp_derrick)
        self.frm.addRow("GLE", self.sp_gle); self.frm.addRow("RTE", self.sp_rte); self.frm.addRow("MSL", self.sp_msl)
        self.frm.addRow("KOP1", self.sp_kop1); self.frm.addRow("KOP2", self.sp_kop2)
        self.frm.addRow("Latitude", self.le_lat); self.frm.addRow("Longitude", self.le_lon)
        self.frm.addRow("Northing", self.le_northing); self.frm.addRow("Easting", self.le_easting)
        self.frm.addRow("Hole Size (in)", self.sp_hole_in)
        self.frm.addRow("Estimated Final Depth MD (m)", self.sp_final_md)
        self.frm.addRow("Offshore Water Depth (m)", self.sp_wd)
        self.frm.addRow("Spud Date", self.dt_spud); self.frm.addRow("Start Hole Date", self.dt_start_hole); self.frm.addRow("Rig Move Date", self.dt_rig_move)

        root.addLayout(self.frm)
        act = QHBoxLayout(); self.btn_save = QPushButton("Save Well"); self.btn_delete = QPushButton("Delete Well")
        self.btn_save.clicked.connect(self._save_well); self.btn_delete.clicked.connect(self._delete_well)
        act.addWidget(self.btn_save); act.addWidget(self.btn_delete); root.addLayout(act)

    def _load_companies(self):
        self.cb_company.clear()
        with self.db.get_session() as s:
            rows = s.query(Company).order_by(Company.name).all()
        for r in rows: self.cb_company.addItem(r.name, r.id)
        self._on_company_changed()

    def _on_company_changed(self):
        self.cb_project.clear()
        cid = self.cb_company.currentData()
        if cid is None: return
        with self.db.get_session() as s:
            pros = s.query(Project).filter_by(company_id=cid).order_by(Project.name).all()
        for p in pros: self.cb_project.addItem(p.name, p.id)
        self._on_project_changed()

    def _on_project_changed(self):
        self.cb_well.clear()
        pid = self.cb_project.currentData()
        if pid is None: return
        with self.db.get_session() as s:
            wells = s.query(Well).filter_by(project_id=pid).order_by(Well.name).all()
        for w in wells: self.cb_well.addItem(w.name, w.id)
        self._on_well_changed()

    def _on_well_changed(self):
        self.cb_section.clear()
        wid = self.cb_well.currentData()
        if wid is None: return
        with self.db.get_session() as s:
            secs = s.query(Section).filter_by(well_id=wid).order_by(Section.name).all()
            w = s.query(Well).get(wid)
        for sc in secs: self.cb_section.addItem(sc.name, sc.id)
        # fill form
        if w:
            self.le_well_name.setText(w.name or '')
            self.le_rig_name.setText(w.rig_name or '')
            self.le_operator.setText(w.operator or '')
            self.le_field.setText(w.project.field if w.project and w.project.field else '')
            self.cb_well_type.setCurrentIndex(0 if (w.well_type or '').lower()=="onshore" else 1)
            self.cb_rig_type.setCurrentText(w.rig_type or "Land")
            self.cb_shape.setCurrentText(w.well_shape or "Vertical")
            self.sp_derrick.setValue(w.derrick_height_ft or 0)
            self.sp_gle.setValue(w.gle or 0); self.sp_rte.setValue(w.rte or 0); self.sp_msl.setValue(w.msl or 0)
            self.sp_kop1.setValue(w.kop1 or 0); self.sp_kop2.setValue(w.kop2 or 0)
            self.le_lat.setText(w.lat or ''); self.le_lon.setText(w.lon or '')
            self.le_northing.setText(w.northing or ''); self.le_easting.setText(w.easting or '')
            self.sp_hole_in.setValue(w.hole_size_in or 0); self.sp_final_md.setValue(w.final_depth_md_m or 0)
            self.sp_wd.setValue(w.offshore_water_depth_m or 0)
            if w.spud_date: self.dt_spud.setDate(QDate(w.spud_date.year, w.spud_date.month, w.spud_date.day))
            if w.start_hole_date: self.dt_start_hole.setDate(QDate(w.start_hole_date.year, w.start_hole_date.month, w.start_hole_date.day))
            if w.rig_move_date: self.dt_rig_move.setDate(QDate(w.rig_move_date.year, w.rig_move_date.month, w.rig_move_date.day))

    def _add_company(self):
        name = self._quick_text("New Company Name")
        if not name: return
        with self.db.get_session() as s: s.add(Company(name=name))
        self._load_companies()

    def _add_project(self):
        cid = self.cb_company.currentData()
        if cid is None: return
        name = self._quick_text("New Project Name")
        if not name: return
        with self.db.get_session() as s: s.add(Project(company_id=cid, name=name))
        self._on_company_changed()

    def _add_well(self):
        pid = self.cb_project.currentData()
        if pid is None: return
        name = self._quick_text("New Well Name")
        if not name: return
        with self.db.get_session() as s: s.add(Well(project_id=pid, name=name))
        self._on_project_changed()

    def _add_section(self):
        wid = self.cb_well.currentData()
        if wid is None: return
        name = self._quick_text("New Section Name")
        if not name: return
        with self.db.get_session() as s: s.add(Section(well_id=wid, name=name))
        self._on_well_changed()

    def _quick_text(self, title):
        from PySide2.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, title, "Enter text")
        return text.strip() if ok and text.strip() else None

    def _save_well(self):
        wid = self.cb_well.currentData()
        if wid is None: return
        with self.db.get_session() as s:
            w = s.query(Well).get(wid)
            if not w: return
            w.name = self.le_well_name.text().strip()
            w.rig_name = self.le_rig_name.text().strip()
            w.operator = self.le_operator.text().strip()
            w.well_type = self.cb_well_type.currentText()
            w.rig_type = self.cb_rig_type.currentText()
            w.well_shape = self.cb_shape.currentText()
            w.derrick_height_ft = self.sp_derrick.value()
            w.gle = self.sp_gle.value(); w.rte = self.sp_rte.value(); w.msl = self.sp_msl.value()
            w.kop1 = self.sp_kop1.value(); w.kop2 = self.sp_kop2.value()
            w.lat = self.le_lat.text().strip(); w.lon = self.le_lon.text().strip()
            w.northing = self.le_northing.text().strip(); w.easting = self.le_easting.text().strip()
            w.hole_size_in = self.sp_hole_in.value(); w.final_depth_md_m = self.sp_final_md.value()
            w.offshore_water_depth_m = self.sp_wd.value()
            w.spud_date = self.dt_spud.date().toPython()
            w.start_hole_date = self.dt_start_hole.date().toPython()
            w.rig_move_date = self.dt_rig_move.date().toPython()
        QMessageBox.information(self, "Saved", "Well info saved.")

    def _delete_well(self):
        wid = self.cb_well.currentData()
        if wid is None: return
        from PySide2.QtWidgets import QMessageBox
        if QMessageBox.question(self, "Confirm", "Delete this well and all its data?") != QMessageBox.Yes:
            return
        with self.db.get_session() as s:
            w = s.query(Well).get(wid)
            if w: s.delete(w)
        self._on_project_changed()

class WellInfoModule(BaseModule):
    DISPLAY_NAME = "Well Info"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = WellInfoWidget(self.db)
    def get_widget(self): return self.widget
