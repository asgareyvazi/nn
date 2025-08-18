
# =========================================
# file: nikan_drill_master/modules/well_info.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QFormLayout, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import QDate
from sqlalchemy.orm import Session
from database import session_scope
from models import Company, Project, Well
from modules.base import ModuleBase

class WellInfoModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        self.form = QFormLayout()
        self.company = QLineEdit()
        self.project = QLineEdit()
        self.well_name = QLineEdit()
        self.rig_name = QLineEdit()
        self.operator = QLineEdit()
        self.field = QLineEdit()

        self.well_type = _combo(self, ["", "Onshore", "Offshore"])
        self.rig_type = _combo(self, ["", "Land", "Jackup", "SemiSub", "Drillship"])
        self.well_shape = _combo(self, ["", "Vertical", "Deviated", "Horizontal"])
        self.derrick_height = QSpinBox(); self.derrick_height.setRange(0, 3000)

        self.gle = QDoubleSpinBox(); self.gle.setRange(-10000, 10000); self.gle.setDecimals(2)
        self.rte = QDoubleSpinBox(); self.rte.setRange(-10000, 10000); self.rte.setDecimals(2)
        self.msl = QDoubleSpinBox(); self.msl.setRange(-10000, 10000); self.msl.setDecimals(2)
        self.kop1 = QDoubleSpinBox(); self.kop1.setRange(-10000, 10000); self.kop1.setDecimals(2)
        self.kop2 = QDoubleSpinBox(); self.kop2.setRange(-10000, 10000); self.kop2.setDecimals(2)

        self.latitude = QLineEdit(); self.longitude = QLineEdit()
        self.northing = QDoubleSpinBox(); self.northing.setRange(-1e9, 1e9); self.northing.setDecimals(3)
        self.easting = QDoubleSpinBox(); self.easting.setRange(-1e9, 1e9); self.easting.setDecimals(3)

        self.hole_size = QDoubleSpinBox(); self.hole_size.setRange(0, 100); self.hole_size.setDecimals(2)
        self.est_final_depth = QDoubleSpinBox(); self.est_final_depth.setRange(0, 1e6); self.est_final_depth.setDecimals(1)
        self.offshore_water_depth = QDoubleSpinBox(); self.offshore_water_depth.setRange(0, 1e5); self.offshore_water_depth.setDecimals(1)

        self.spud_date = QDateEdit(); self.spud_date.setCalendarPopup(True)
        self.start_hole_date = QDateEdit(); self.start_hole_date.setCalendarPopup(True)
        self.rig_move_date = QDateEdit(); self.rig_move_date.setCalendarPopup(True)

        self.supervisor_day = QLineEdit(); self.supervisor_night = QLineEdit()
        self.toolpusher_day = QLineEdit(); self.toolpusher_night = QLineEdit()
        self.operation_manager = QLineEdit()
        self.geologist1 = QLineEdit(); self.geologist2 = QLineEdit()
        self.client_rep = QLineEdit()

        self.objectives = QTextEdit()

        f = self.form
        f.addRow("Company", self.company)
        f.addRow("Project", self.project)
        f.addRow("Well Name", self.well_name)
        f.addRow("Rig Name", self.rig_name)
        f.addRow("Operator", self.operator)
        f.addRow("Field", self.field)
        f.addRow("Well Type", self.well_type)
        f.addRow("Rig Type", self.rig_type)
        f.addRow("Well Shape", self.well_shape)
        f.addRow("Derrick Height (ft)", self.derrick_height)
        f.addRow("GLE", self.gle); f.addRow("RTE", self.rte); f.addRow("MSL", self.msl)
        f.addRow("KOP1", self.kop1); f.addRow("KOP2", self.kop2)
        f.addRow("Latitude", self.latitude); f.addRow("Longitude", self.longitude)
        f.addRow("Northing", self.northing); f.addRow("Easting", self.easting)
        f.addRow("Hole Size (in)", self.hole_size)
        f.addRow("Est. Final Depth MD (m)", self.est_final_depth)
        f.addRow("Offshore Water Depth (m)", self.offshore_water_depth)
        f.addRow("Spud Date", self.spud_date)
        f.addRow("Start Hole Date", self.start_hole_date)
        f.addRow("Rig Move Date", self.rig_move_date)
        f.addRow("Supervisors (Day/Night)", _row2(self.supervisor_day, self.supervisor_night))
        f.addRow("Toolpusher (Day/Night)", _row2(self.toolpusher_day, self.toolpusher_night))
        f.addRow("Operation Manager", self.operation_manager)
        f.addRow("Geologist (1/2)", _row2(self.geologist1, self.geologist2))
        f.addRow("Client Rep", self.client_rep)
        f.addRow("Objectives", self.objectives)

        save_btn = QPushButton("Save / Upsert")
        save_btn.clicked.connect(self._save)
        lay.addLayout(self.form); lay.addWidget(save_btn)

    def _save(self):
        company_name = self.company.text().strip()
        project_name = self.project.text().strip()
        well_name = self.well_name.text().strip()
        if not (company_name and project_name and well_name):
            QMessageBox.warning(self, "Validation", "Company, Project, Well Name اجباری است")
            return

        with session_scope(self.SessionLocal) as s:
            comp = s.query(Company).filter(Company.name == company_name).one_or_none()
            if not comp:
                comp = Company(name=company_name)
                s.add(comp); s.flush()
            proj = s.query(Project).filter(Project.company_id == comp.id, Project.name == project_name).one_or_none()
            if not proj:
                proj = Project(company_id=comp.id, name=project_name)
                s.add(proj); s.flush()
            well = s.query(Well).filter(Well.project_id == proj.id, Well.name == well_name).one_or_none()
            if not well:
                well = Well(project_id=proj.id, name=well_name)
                s.add(well)

            # set fields
            well.rig_name = self.rig_name.text().strip() or None
            well.operator = self.operator.text().strip() or None
            well.field_name = self.field.text().strip() or None
            well.well_type = self.well_type.currentText() or None
            well.rig_type = self.rig_type.currentText() or None
            well.well_shape = self.well_shape.currentText() or None
            well.derrick_height_ft = self.derrick_height.value() or None

            well.gle = self.gle.value() or None; well.rte = self.rte.value() or None; well.msl = self.msl.value() or None
            well.kop1 = self.kop1.value() or None; well.kop2 = self.kop2.value() or None

            well.latitude = self.latitude.text().strip() or None
            well.longitude = self.longitude.text().strip() or None
            well.northing = self.northing.value() or None
            well.easting = self.easting.value() or None

            well.hole_size_in = self.hole_size.value() or None
            well.est_final_depth_md_m = self.est_final_depth.value() or None
            well.offshore_water_depth_m = self.offshore_water_depth.value() or None

            well.spud_date = self.spud_date.date().toPython()
            well.start_hole_date = self.start_hole_date.date().toPython()
            well.rig_move_date = self.rig_move_date.date().toPython()

            well.supervisor_day = self.supervisor_day.text().strip() or None
            well.supervisor_night = self.supervisor_night.text().strip() or None
            well.toolpusher_day = self.toolpusher_day.text().strip() or None
            well.toolpusher_night = self.toolpusher_night.text().strip() or None
            well.operation_manager = self.operation_manager.text().strip() or None
            well.geologist1 = self.geologist1.text().strip() or None
            well.geologist2 = self.geologist2.text().strip() or None
            well.client_rep = self.client_rep.text().strip() or None
            well.objectives = self.objectives.toPlainText().strip() or None

        QMessageBox.information(self, "Saved", "Well Info ذخیره شد")

def _combo(parent, items: list[str]):
    cb = QComboBox(parent)
    for it in items:
        cb.addItem(it)
    return cb

def _row2(a: QWidget, b: QWidget):
    w = QWidget()
    lay = QVBoxLayout(w); lay.setContentsMargins(0,0,0,0)
    lay.addWidget(a); lay.addWidget(b)
    return w
