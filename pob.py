# File: modules/pob.py
# Purpose: Personnel On Board table (client/contractor/service buckets).

from PySide2.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, Crew

class POBWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.tbl = QTableWidget(0,4); self.tbl.setHorizontalHeaderLabels(["Name/Service","No.","Date IN","Total POB"])
        self.l.addWidget(self.tbl)
        h = QHBoxLayout(); self.btn_add = QPushButton("Add"); self.btn_del = QPushButton("Delete"); self.btn_save = QPushButton("Save")
        h.addWidget(self.btn_add); h.addWidget(self.btn_del); h.addWidget(self.btn_save); self.l.addLayout(h)
        self.btn_add.clicked.connect(self._add); self.btn_del.clicked.connect(self._del); self.btn_save.clicked.connect(self._save)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        for c in range(4): self.tbl.setItem(r,c,QTableWidgetItem(""))

    def _del(self):
        for r in sorted([i.row() for i in self.tbl.selectionModel().selectedRows()], reverse=True): self.tbl.removeRow(r)

    def _load(self):
        sid = self.cb_section.currentData(); self.tbl.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            rows = s.query(Crew).filter_by(section_id=sid).all()
        for c in rows:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r,0,QTableWidgetItem(c.company or "")); self.tbl.setItem(r,1,QTableWidgetItem(str(c.count or 0))); self.tbl.setItem(r,2,QTableWidgetItem(str(c.date_in or ""))); self.tbl.setItem(r,3,QTableWidgetItem(str(c.total_pob or "")))

    def _save(self):
        sid = self.cb_section.currentData(); 
        if sid is None: return
        with self.db.get_session() as s:
            for rec in s.query(Crew).filter_by(section_id=sid).all(): s.delete(rec)
            for r in range(self.tbl.rowCount()):
                name = self.tbl.item(r,0).text().strip() if self.tbl.item(r,0) else ''
                if not name: continue
                try: count = int(float(self.tbl.item(r,1).text()))
                except: count = 0
                date_in = self.tbl.item(r,2).text().strip() if self.tbl.item(r,2) else None
                total_pob = None
                try: total_pob = int(float(self.tbl.item(r,3).text()))
                except: total_pob = None
                s.add(Crew(section_id=sid, company=name, service="", count=count, date_in=date_in, total_pob=total_pob))
        QMessageBox.information(self, "Saved", "POB saved.")

class POBModule(BaseModule):
    DISPLAY_NAME = "POB"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = POBWidget(self.db)
    def get_widget(self): return self.widget
