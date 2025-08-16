# File: modules/npt_report.py
# Purpose: NPT time range entries with code/sub-code and responsible party.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QMessageBox
from .base import BaseModule
from models import Section, NPTEntry, MainCode, SubCode

class NPTReportWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        v = QVBoxLayout(self)
        self.cb_section = QComboBox(); v.addWidget(self.cb_section)
        self.tbl = QTableWidget(0,6); self.tbl.setHorizontalHeaderLabels(["From","To","MainCode","SubCode","Description","Responsible"])
        v.addWidget(self.tbl)
        h = QHBoxLayout(); self.btn_add=QPushButton("Add Row"); self.btn_del=QPushButton("Delete Selected"); self.btn_save=QPushButton("Save")
        for b in (self.btn_add,self.btn_del,self.btn_save): h.addWidget(b); v.addLayout(h)
        self.btn_add.clicked.connect(self._add); self.btn_del.clicked.connect(self._del); self.btn_save.clicked.connect(self._save)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        for c in range(6): self.tbl.setItem(r,c,QTableWidgetItem(""))

    def _del(self):
        for i in sorted([x.row() for x in self.tbl.selectionModel().selectedRows()], reverse=True): self.tbl.removeRow(i)

    def _load(self):
        sid = self.cb_section.currentData(); self.tbl.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            rows = s.query(NPTEntry).filter_by(section_id=sid).all()
        for e in rows:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r,0,QTableWidgetItem(e.from_time or "")); self.tbl.setItem(r,1,QTableWidgetItem(e.to_time or ""))
            self.tbl.setItem(r,2,QTableWidgetItem(str(e.main_code.code if e.main_code else "")))
            self.tbl.setItem(r,3,QTableWidgetItem(str(e.sub_code.code if e.sub_code else "")))
            self.tbl.setItem(r,4,QTableWidgetItem(e.description or "")); self.tbl.setItem(r,5,QTableWidgetItem(e.responsible or ""))

    def _save(self):
        sid = self.cb_section.currentData(); if sid is None: return
        with self.db.get_session() as s:
            for e in s.query(NPTEntry).filter_by(section_id=sid).all(): s.delete(e)
            # map codes
            mains = {m.code:str(m.id) for m in s.query(MainCode).all()}
            subs_by_code = {f"{sc.main_code.code}/{sc.code}":sc.id for sc in s.query(SubCode).join(MainCode).all()}
            for r in range(self.tbl.rowCount()):
                fr = self.tbl.item(r,0).text().strip() if self.tbl.item(r,0) else ''
                to = self.tbl.item(r,1).text().strip() if self.tbl.item(r,1) else ''
                mc_code = self.tbl.item(r,2).text().strip() if self.tbl.item(r,2) else ''
                sc_code = self.tbl.item(r,3).text().strip() if self.tbl.item(r,3) else ''
                desc = self.tbl.item(r,4).text().strip() if self.tbl.item(r,4) else ''
                resp = self.tbl.item(r,5).text().strip() if self.tbl.item(r,5) else ''
                mc_id = None
                for k,v in mains.items():
                    if k == mc_code: mc_id = int(v); break
                sc_id = None
                # try combined key MAIN/SUB
                for k,v in subs_by_code.items():
                    if k.endswith("/"+sc_code): sc_id=v
                s.add(NPTEntry(section_id=sid, from_time=fr, to_time=to, main_code_id=mc_id, sub_code_id=sc_id, description=desc, responsible=resp))
        QMessageBox.information(self, "Saved", "NPT report saved.")

class NPTReportModule(BaseModule):
    DISPLAY_NAME = "NPT Report"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = NPTReportWidget(self.db)
    def get_widget(self): return self.widget
