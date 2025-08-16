# File: modules/mud_report.py
# Purpose: Mud properties + volumes + chemicals table with add/remove rows.

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QSpinBox
)
from .base import BaseModule
from models import Section, MudReport, MudChemical

class MudReportWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections(); self.current_report=None

    def _build(self):
        v = QVBoxLayout(self)
        self.cb_section=QComboBox(); v.addWidget(self.cb_section)
        frm = QFormLayout(); v.addLayout(frm)

        self.le_mud_type=QLineEdit(); self.le_sample_time=QLineEdit()
        self.mw=QDoubleSpinBox(); self.pv=QDoubleSpinBox(); self.yp=QDoubleSpinBox(); self.funnel=QDoubleSpinBox()
        self.g10s=QDoubleSpinBox(); self.g10m=QDoubleSpinBox(); self.g30m=QDoubleSpinBox()
        self.fl=QDoubleSpinBox(); self.cake=QDoubleSpinBox()
        self.ca=QDoubleSpinBox(); self.chloride=QDoubleSpinBox(); self.kcl=QDoubleSpinBox()
        self.ph=QDoubleSpinBox(); self.hard=QDoubleSpinBox(); self.mbt=QDoubleSpinBox()
        self.solids=QDoubleSpinBox(); self.oil=QDoubleSpinBox(); self.water=QDoubleSpinBox(); self.glycol=QDoubleSpinBox()
        self.temp=QDoubleSpinBox(); self.pf=QDoubleSpinBox(); self.mf=QDoubleSpinBox()
        for w in [self.mw,self.pv,self.yp,self.funnel,self.g10s,self.g10m,self.g30m,self.fl,self.cake,self.ca,self.chloride,self.kcl,
                  self.ph,self.hard,self.mbt,self.solids,self.oil,self.water,self.glycol,self.temp,self.pf,self.mf]:
            w.setRange(0, 1e6); w.setDecimals(2)

        frm.addRow("Mud Type", self.le_mud_type); frm.addRow("Sample Time (HH:mm)", self.le_sample_time)
        frm.addRow("MW (PCF)", self.mw); frm.addRow("PV / YP / Funnel", self._triple(self.pv, self.yp, self.funnel))
        frm.addRow("Gel 10s/10m/30m", self._triple(self.g10s, self.g10m, self.g30m))
        frm.addRow("FL (API) / Cake", self._triple(self.fl, self.cake, QDoubleSpinBox()))
        frm.addRow("Ca / Chloride / KCl", self._triple(self.ca, self.chloride, self.kcl))
        frm.addRow("pH / Hardness / MBT", self._triple(self.ph, self.hard, self.mbt))
        frm.addRow("Solid% / Oil% / Water%", self._triple(self.solids, self.oil, self.water))
        frm.addRow("Glycol% / Temp / Pf/Mf", self._triple(self.glycol, self.temp, self.pf))

        # Volumes
        self.vol_in_hole=QDoubleSpinBox(); self.total_circ=QDoubleSpinBox(); self.loss_dh=QDoubleSpinBox(); self.loss_surf=QDoubleSpinBox()
        self.suction_vol=QDoubleSpinBox(); self.suction_mw=QDoubleSpinBox()
        self.reserve_vol=QDoubleSpinBox(); self.reserve_mw=QDoubleSpinBox()
        self.degasser=QDoubleSpinBox(); self.desander=QDoubleSpinBox(); self.desilter=QDoubleSpinBox()
        self.middle=QDoubleSpinBox(); self.trip_tank=QDoubleSpinBox(); self.sand_trap=QDoubleSpinBox()
        for w in [self.vol_in_hole,self.total_circ,self.loss_dh,self.loss_surf,self.suction_vol,self.suction_mw,self.reserve_vol,self.reserve_mw,
                  self.degasser,self.desander,self.desilter,self.middle,self.trip_tank,self.sand_trap]:
            w.setRange(0, 1e6); w.setDecimals(2)

        frm.addRow("Vol in Hole / Total Circ.", self._pair(self.vol_in_hole, self.total_circ))
        frm.addRow("Loss Downhole / Surface", self._pair(self.loss_dh, self.loss_surf))
        frm.addRow("Suction Tank Vol/MW", self._pair(self.suction_vol, self.suction_mw))
        frm.addRow("Reserve Tank Vol/MW", self._pair(self.reserve_vol, self.reserve_mw))
        frm.addRow("Degasser / Desander / Desilter", self._triple(self.degasser, self.desander, self.desilter))
        frm.addRow("Middle / Trip Tank / Sand Trap", self._triple(self.middle, self.trip_tank, self.sand_trap))

        # Chemicals table
        self.tbl = QTableWidget(0,5); self.tbl.setHorizontalHeaderLabels(["Product","Received","Used","Stock","Unit"])
        hb = QHBoxLayout(); self.btn_add = QPushButton("Add Chemical"); self.btn_del = QPushButton("Delete Selected")
        self.btn_add.clicked.connect(self._add_row); self.btn_del.clicked.connect(self._del_row); hb.addWidget(self.btn_add); hb.addWidget(self.btn_del)
        v.addLayout(hb); v.addWidget(self.tbl)

        btn_save = QPushButton("Save Report"); btn_save.clicked.connect(self._save); v.addWidget(btn_save)
        self.cb_section.currentIndexChanged.connect(self._load_for_section)

    def _pair(self, a, b):
        from PySide2.QtWidgets import QWidget, QHBoxLayout
        w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(0,0,0,0); l.addWidget(a); l.addWidget(b); return w
    def _triple(self, a,b,c):
        from PySide2.QtWidgets import QWidget, QHBoxLayout
        w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(0,0,0,0); [l.addWidget(x) for x in (a,b,c)]; return w

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).order_by(Section.id.desc()).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _load_for_section(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            rep = s.query(MudReport).filter_by(section_id=sid).first()
        self.current_report = rep
        # reset UI
        if not rep:
            self.le_mud_type.clear(); self.le_sample_time.clear()
            for w in [self.mw,self.pv,self.yp,self.funnel,self.g10s,self.g10m,self.g30m,self.fl,self.cake,self.ca,self.chloride,self.kcl,
                      self.ph,self.hard,self.mbt,self.solids,self.oil,self.water,self.glycol,self.temp,self.pf,self.mf,
                      self.vol_in_hole,self.total_circ,self.loss_dh,self.loss_surf,self.suction_vol,self.suction_mw,
                      self.reserve_vol,self.reserve_mw,self.degasser,self.desander,self.desilter,self.middle,self.trip_tank,self.sand_trap]:
                w.setValue(0)
            self.tbl.setRowCount(0)
            return
        # load vals
        self.le_mud_type.setText(rep.mud_type or ''); self.le_sample_time.setText(rep.sample_time or '')
        self.mw.setValue(rep.mw_pcf or 0); self.pv.setValue(rep.pv or 0); self.yp.setValue(rep.yp or 0); self.funnel.setValue(rep.funnel_vis or 0)
        self.g10s.setValue(rep.gel_10s or 0); self.g10m.setValue(rep.gel_10m or 0); self.g30m.setValue(rep.gel_30m or 0)
        self.fl.setValue(rep.fl_api or 0); self.cake.setValue(rep.cake_thickness or 0)
        self.ca.setValue(rep.ca or 0); self.chloride.setValue(rep.chloride or 0); self.kcl.setValue(rep.kcl or 0)
        self.ph.setValue(rep.ph or 0); self.hard.setValue(rep.hardness or 0); self.mbt.setValue(rep.mbt or 0)
        self.solids.setValue(rep.solids_pct or 0); self.oil.setValue(rep.oil_pct or 0); self.water.setValue(rep.water_pct or 0); self.glycol.setValue(rep.glycol_pct or 0)
        self.temp.setValue(rep.temp_c or 0); self.pf.setValue(rep.pf or 0); self.mf.setValue(rep.mf or 0)
        self.vol_in_hole.setValue(rep.vol_in_hole or 0); self.total_circ.setValue(rep.total_circulated or 0)
        self.loss_dh.setValue(rep.loss_downhole or 0); self.loss_surf.setValue(rep.loss_surface or 0)
        self.suction_vol.setValue(rep.suction_tank_vol or 0); self.suction_mw.setValue(rep.suction_tank_mw or 0)
        self.reserve_vol.setValue(rep.reserve_tank_vol or 0); self.reserve_mw.setValue(rep.reserve_tank_mw or 0)
        self.degasser.setValue(rep.degasser or 0); self.desander.setValue(rep.desander or 0); self.desilter.setValue(rep.desilter or 0)
        self.middle.setValue(rep.middle or 0); self.trip_tank.setValue(rep.trip_tank or 0); self.sand_trap.setValue(rep.sand_trap or 0)

        self.tbl.setRowCount(0)
        for ch in rep.chemicals:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r, 0, QTableWidgetItem(ch.product_type or ''))
            self.tbl.setItem(r, 1, QTableWidgetItem(str(ch.received or 0)))
            self.tbl.setItem(r, 2, QTableWidgetItem(str(ch.used or 0)))
            self.tbl.setItem(r, 3, QTableWidgetItem(str(ch.stock or 0)))
            self.tbl.setItem(r, 4, QTableWidgetItem(ch.unit or ''))

    def _add_row(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        for c in range(5): self.tbl.setItem(r, c, QTableWidgetItem(""))

    def _del_row(self):
        sel = self.tbl.selectionModel().selectedRows()
        for idx in sorted([i.row() for i in sel], reverse=True): self.tbl.removeRow(idx)

    def _save(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            rep = s.query(MudReport).filter_by(section_id=sid).first()
            if not rep:
                rep = MudReport(section_id=sid); s.add(rep)
            rep.mud_type = self.le_mud_type.text().strip(); rep.sample_time = self.le_sample_time.text().strip()
            rep.mw_pcf=self.mw.value(); rep.pv=self.pv.value(); rep.yp=self.yp.value(); rep.funnel_vis=self.funnel.value()
            rep.gel_10s=self.g10s.value(); rep.gel_10m=self.g10m.value(); rep.gel_30m=self.g30m.value()
            rep.fl_api=self.fl.value(); rep.cake_thickness=self.cake.value()
            rep.ca=self.ca.value(); rep.chloride=self.chloride.value(); rep.kcl=self.kcl.value()
            rep.ph=self.ph.value(); rep.hardness=self.hard.value(); rep.mbt=self.mbt.value()
            rep.solids_pct=self.solids.value(); rep.oil_pct=self.oil.value(); rep.water_pct=self.water.value(); rep.glycol_pct=self.glycol.value()
            rep.temp_c=self.temp.value(); rep.pf=self.pf.value(); rep.mf=self.mf.value()
            rep.vol_in_hole=self.vol_in_hole.value(); rep.total_circulated=self.total_circ.value()
            rep.loss_downhole=self.loss_dh.value(); rep.loss_surface=self.loss_surf.value()
            rep.suction_tank_vol=self.suction_vol.value(); rep.suction_tank_mw=self.suction_mw.value()
            rep.reserve_tank_vol=self.reserve_vol.value(); rep.reserve_tank_mw=self.reserve_mw.value()
            rep.degasser=self.degasser.value(); rep.desander=self.desander.value(); rep.desilter=self.desilter.value()
            rep.middle=self.middle.value(); rep.trip_tank=self.trip_tank.value(); rep.sand_trap=self.sand_trap.value()

            # chemicals
            # clear and recreate (simpler; acceptable for report-scale data)
            for ch in list(rep.chemicals): s.delete(ch)
            for r in range(self.tbl.rowCount()):
                prod = self.tbl.item(r,0).text().strip() if self.tbl.item(r,0) else ''
                if not prod: continue
                def _num(c):
                    try: return float(self.tbl.item(r,c).text())
                    except: return 0.0
                s.add(MudChemical(
                    report=rep, product_type=prod,
                    received=_num(1), used=_num(2), stock=_num(3),
                    unit=(self.tbl.item(r,4).text().strip() if self.tbl.item(r,4) else '')
                ))
        QMessageBox.information(self, "Saved", "Mud report saved.")

class MudReportModule(BaseModule):
    DISPLAY_NAME = "Mud Report"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = MudReportWidget(self.db)
    def get_widget(self): return self.widget
