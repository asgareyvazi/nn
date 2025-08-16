# File: modules/bit_record.py
# Purpose: Bit master + per-bit run report (before/after photo paths).

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from .base import BaseModule
from models import Section, BitRecord, BitRunReport

class BitRecordWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections(); self.current_bit=None

    def _build(self):
        v = QVBoxLayout(self)
        self.cb_section=QComboBox(); v.addWidget(self.cb_section)
        frm = QFormLayout(); v.addLayout(frm)
        self.le_bit_no=QLineEdit(); self.sp_size=QDoubleSpinBox(); self.sp_size.setRange(0,60); self.le_manu=QLineEdit()
        self.le_type=QLineEdit(); self.le_sn=QLineEdit(); self.le_iadc=QLineEdit(); self.le_dull=QLineEdit(); self.le_reason=QLineEdit()
        self.sp_in=QDoubleSpinBox(); self.sp_out=QDoubleSpinBox(); self.sp_hours=QDoubleSpinBox()
        self.sp_cum_drilled=QDoubleSpinBox(); self.sp_cum_hours=QDoubleSpinBox(); self.sp_rop=QDoubleSpinBox()
        for w in [self.sp_size,self.sp_in,self.sp_out,self.sp_hours,self.sp_cum_drilled,self.sp_cum_hours,self.sp_rop]:
            w.setRange(0, 1e6); w.setDecimals(2)
        self.le_formation=QLineEdit(); self.le_lith=QLineEdit()
        frm.addRow("Bit No", self.le_bit_no); frm.addRow("Size (in)", self.sp_size); frm.addRow("Manufacturer", self.le_manu)
        frm.addRow("Type", self.le_type); frm.addRow("Serial No", self.le_sn); frm.addRow("IADC Code", self.le_iadc)
        frm.addRow("Dull Grading", self.le_dull); frm.addRow("Reason Pulled", self.le_reason)
        frm.addRow("Depth In/Out", self._pair(self.sp_in, self.sp_out)); frm.addRow("Hours / Cum Drilled / Cum Hrs / ROP", self._quad(self.sp_hours, self.sp_cum_drilled, self.sp_cum_hours, self.sp_rop))
        frm.addRow("Formation / Lithology", self._pair(self.le_formation, self.le_lith))

        # runs
        self.tbl = QTableWidget(0,10); self.tbl.setHorizontalHeaderLabels(["WOB","RPM","Flowrate","SPP","PV","YP","Cum Drill","ROP","TFA","Revolution"])
        hb = QHBoxLayout(); self.btn_add=QPushButton("Add Run"); self.btn_del=QPushButton("Delete Selected"); hb.addWidget(self.btn_add); hb.addWidget(self.btn_del); v.addLayout(hb); v.addWidget(self.tbl)
        self.btn_add.clicked.connect(self._add_run); self.btn_del.clicked.connect(self._del_run)

        save = QPushButton("Save Bit"); save.clicked.connect(self._save); v.addWidget(save)

    def _pair(self, a,b):
        from PySide2.QtWidgets import QWidget, QHBoxLayout
        w=QWidget(); l=QHBoxLayout(w); l.setContentsMargins(0,0,0,0); l.addWidget(a); l.addWidget(b); return w
    def _quad(self, a,b,c,d):
        from PySide2.QtWidgets import QWidget, QHBoxLayout
        w=QWidget(); l=QHBoxLayout(w); l.setContentsMargins(0,0,0,0); [l.addWidget(x) for x in (a,b,c,d)]; return w

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _add_run(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        for c in range(10): self.tbl.setItem(r, c, QTableWidgetItem("0"))

    def _del_run(self):
        sel = self.tbl.selectionModel().selectedRows()
        for i in sorted([x.row() for x in sel], reverse=True): self.tbl.removeRow(i)

    def _save(self):
        sid = self.cb_section.currentData(); if sid is None: return
        with self.db.get_session() as s:
            bit = BitRecord(section_id=sid)
            bit.bit_no=self.le_bit_no.text().strip(); bit.size_in=self.sp_size.value(); bit.manufacturer=self.le_manu.text().strip()
            bit.type=self.le_type.text().strip(); bit.serial_no=self.le_sn.text().strip()
            bit.iadc_code=self.le_iadc.text().strip(); bit.dull_grading=self.le_dull.text().strip(); bit.reason_pulled=self.le_reason.text().strip()
            bit.depth_in=self.sp_in.value(); bit.depth_out=self.sp_out.value(); bit.hours=self.sp_hours.value()
            bit.cum_drilled=self.sp_cum_drilled.value(); bit.cum_hours=self.sp_cum_hours.value(); bit.rop=self.sp_rop.value()
            bit.formation=self.le_formation.text().strip(); bit.lithology=self.le_lith.text().strip()
            s.add(bit); s.flush()
            for r in range(self.tbl.rowCount()):
                def n(c):
                    try: return float(self.tbl.item(r,c).text())
                    except: return 0.0
                s.add(BitRunReport(
                    bit_id=bit.id, wob=n(0), rpm=n(1), flowrate=n(2), spp=n(3), pv=n(4), yp=n(5),
                    cumulative_drilling=n(6), rop=n(7), tfa=n(8), revolution=n(9)
                ))
        QMessageBox.information(self, "Saved", "Bit record saved with runs.")

class BitRecordModule(BaseModule):
    DISPLAY_NAME = "Bit Record"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = BitRecordWidget(self.db)
    def get_widget(self): return self.widget
