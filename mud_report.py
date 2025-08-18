
# =========================================
# file: nikan_drill_master/modules/mud_report.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QComboBox, QTimeEdit, QDoubleSpinBox, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
from sqlalchemy.orm import Session
from modules.base import ModuleBase
from database import session_scope
from models import MudReport, MudChemical, DailyReport

class MudReportModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.mud_type = QComboBox(); self.mud_type.addItems(["", "WBM", "OBM", "SBM"])
        self.sample_time = QTimeEdit()
        def spin(dec=2, rng=(-1e6, 1e6)):
            s = QDoubleSpinBox(); s.setDecimals(dec); s.setRange(*rng); return s
        self.mw_pcf = spin(); self.pv = spin(); self.yp = spin(); self.funnel_vis = spin()
        self.gel_10s = spin(); self.gel_10m = spin(); self.gel_30m = spin()
        self.fl_api = spin(); self.cake = spin()
        self.ca = spin(); self.cl = spin(); self.kcl = spin(); self.ph = spin(); self.hardness = spin(); self.mbt = spin()
        self.solid = spin(); self.oil = spin(); self.water = spin(); self.glycol = spin(); self.temp = spin(); self.pf = spin(); self.mf = spin()
        self.vol_in_hole = spin(); self.total_circ = spin(); self.loss_down = spin(); self.loss_surf = spin()

        for label, w in [
            ("Mud Type", self.mud_type), ("Sample Time", self.sample_time),
            ("MW(PCF)", self.mw_pcf), ("PV", self.pv), ("YP", self.yp), ("Funnel Vis", self.funnel_vis),
            ("Gel 10s/10m/30m", _row3(self.gel_10s, self.gel_10m, self.gel_30m)),
            ("FL(API)", self.fl_api), ("Cake Thickness", self.cake),
            ("Ca", self.ca), ("Chloride", self.cl), ("KCl", self.kcl), ("pH", self.ph), ("Hardness", self.hardness), ("MBT", self.mbt),
            ("Solid %", self.solid), ("Oil %", self.oil), ("Water %", self.water), ("Glycol %", self.glycol), ("Temp", self.temp),
            ("Pf/Mf", _row2(self.pf, self.mf)),
            ("Volumes: InHole/TotalCirc/Loss(DH/SURF)", _row4(self.vol_in_hole, self.total_circ, self.loss_down, self.loss_surf))
        ]:
            form.addRow(label, w)
        lay.addLayout(form)

        # chemicals
        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels(["Product Type", "Received", "Used", "Stock", "Unit"])
        btns = QHBoxLayout()
        add = QPushButton("Add Row"); rm = QPushButton("Delete Row"); save = QPushButton("Save")
        add.clicked.connect(lambda: self.tbl.insertRow(self.tbl.rowCount()))
        rm.clicked.connect(lambda: self.tbl.removeRow(self.tbl.currentRow()))
        save.clicked.connect(self._save)
        btns.addWidget(add); btns.addWidget(rm); btns.addStretch(1); btns.addWidget(save)
        lay.addLayout(btns); lay.addWidget(self.tbl)

    def _save(self):
        with session_scope(self.SessionLocal) as s:
            dr = s.query(DailyReport).order_by(DailyReport.report_date.desc()).first()
            if not dr:
                QMessageBox.warning(self, "No DR", "ابتدا Daily Report بسازید")
                return
            mr = dr.mud_report
            if not mr:
                from datetime import time
                mr = MudReport(daily_report_id=dr.id, sample_time=time(0,0))
                s.add(mr); s.flush()

            mr.mud_type = self.mud_type.currentText() or None
            mr.sample_time = self.sample_time.time().toPython()
            mr.mw_pcf = self.mw_pcf.value(); mr.pv = self.pv.value(); mr.yp = self.yp.value(); mr.funnel_vis = self.funnel_vis.value()
            mr.gel_10s = self.gel_10s.value(); mr.gel_10m = self.gel_10m.value(); mr.gel_30m = self.gel_30m.value()
            mr.fl_api = self.fl_api.value(); mr.cake_thickness = self.cake.value()
            mr.ca = self.ca.value(); mr.chloride = self.cl.value(); mr.kcl = self.kcl.value(); mr.ph = self.ph.value(); mr.hardness = self.hardness.value(); mr.mbt = self.mbt.value()
            mr.solid_pct = self.solid.value(); mr.oil_pct = self.oil.value(); mr.water_pct = self.water.value(); mr.glycol_pct = self.glycol.value(); mr.temp_c = self.temp.value()
            mr.pf = self.pf.value(); mr.mf = self.mf.value()
            mr.vol_in_hole = self.vol_in_hole.value(); mr.total_circulated = self.total_circ.value(); mr.loss_downhole = self.loss_down.value(); mr.loss_surface = self.loss_surf.value()

            s.query(MudChemical).filter(MudChemical.mud_report_id==mr.id).delete()
            s.flush()
            for r in range(self.tbl.rowCount()):
                product = self.tbl.item(r,0).text() if self.tbl.item(r,0) else ""
                recv = float(self.tbl.item(r,1).text()) if self.tbl.item(r,1) and self.tbl.item(r,1).text() else None
                used = float(self.tbl.item(r,2).text()) if self.tbl.item(r,2) and self.tbl.item(r,2).text() else None
                stock = float(self.tbl.item(r,3).text()) if self.tbl.item(r,3) and self.tbl.item(r,3).text() else None
                unit = self.tbl.item(r,4).text() if self.tbl.item(r,4) else ""
                if product:
                    s.add(MudChemical(mud_report_id=mr.id, product_type=product, received=recv, used=used, stock=stock, unit=unit or None))
        QMessageBox.information(self, "Saved", "Mud Report ذخیره شد")

def _row2(a, b):
    from PySide6.QtWidgets import QWidget, QHBoxLayout
    w = QWidget(); lay = QHBoxLayout(w); lay.setContentsMargins(0,0,0,0); lay.addWidget(a); lay.addWidget(b); return w

def _row3(a, b, c):
    from PySide6.QtWidgets import QWidget, QHBoxLayout
    w = QWidget(); lay = QHBoxLayout(w); lay.setContentsMargins(0,0,0,0); lay.addWidget(a); lay.addWidget(b); lay.addWidget(c); return w

def _row4(a,b,c,d):
    from PySide6.QtWidgets import QWidget, QHBoxLayout
    w = QWidget(); lay = QHBoxLayout(w); lay.setContentsMargins(0,0,0,0); [lay.addWidget(x) for x in (a,b,c,d)]; return w
