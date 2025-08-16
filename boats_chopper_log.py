# File: modules/boats_chopper_log.py
# Purpose: Boats & Chopper logs.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from .base import BaseModule
from models import Section, BoatLog, ChopperLog

class BoatsChopperWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.tbl_boats = QTableWidget(0,4); self.tbl_boats.setHorizontalHeaderLabels(["Name","Arrival","Departure","Status"])
        self.tbl_choppers = QTableWidget(0,4); self.tbl_choppers.setHorizontalHeaderLabels(["Name","Arrival","Departure","PAX IN"])
        self.l.addWidget(self.tbl_boats); self.l.addWidget(self.tbl_choppers)
        h = QHBoxLayout(); self.btn_save = QPushButton("Save"); self.btn_add = QPushButton("Add Row"); self.btn_del = QPushButton("Delete Selected")
        h.addWidget(self.btn_add); h.addWidget(self.btn_del); h.addWidget(self.btn_save); self.l.addLayout(h)
        self.btn_add.clicked.connect(self._add); self.btn_del.clicked.connect(self._del); self.btn_save.clicked.connect(self._save)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _add(self):
        self.tbl_boats.insertRow(self.tbl_boats.rowCount()); self.tbl_choppers.insertRow(self.tbl_choppers.rowCount())

    def _del(self):
        for tbl in (self.tbl_boats, self.tbl_choppers):
            for r in sorted([i.row() for i in tbl.selectionModel().selectedRows()], reverse=True): tbl.removeRow(r)

    def _load(self):
        sid = self.cb_section.currentData()
        self.tbl_boats.setRowCount(0); self.tbl_choppers.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            boats = s.query(BoatLog).filter_by(section_id=sid).all()
            choppers = s.query(ChopperLog).filter_by(section_id=sid).all()
        for b in boats:
            r = self.tbl_boats.rowCount(); self.tbl_boats.insertRow(r)
            self.tbl_boats.setItem(r,0,QTableWidgetItem(b.name or "")); self.tbl_boats.setItem(r,1,QTableWidgetItem(str(b.arrival or "")))
            self.tbl_boats.setItem(r,2,QTableWidgetItem(str(b.departure or ""))); self.tbl_boats.setItem(r,3,QTableWidgetItem(b.status or ""))
        for c in choppers:
            r = self.tbl_choppers.rowCount(); self.tbl_choppers.insertRow(r)
            self.tbl_choppers.setItem(r,0,QTableWidgetItem(c.name or "")); self.tbl_choppers.setItem(r,1,QTableWidgetItem(str(c.arrival or "")))
            self.tbl_choppers.setItem(r,2,QTableWidgetItem(str(c.departure or ""))); self.tbl_choppers.setItem(r,3,QTableWidgetItem(str(c.pax_in or "")))

    def _save(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            for rec in s.query(BoatLog).filter_by(section_id=sid).all(): s.delete(rec)
            for rec in s.query(ChopperLog).filter_by(section_id=sid).all(): s.delete(rec)
            for r in range(self.tbl_boats.rowCount()):
                name = self.tbl_boats.item(r,0).text().strip() if self.tbl_boats.item(r,0) else ''
                if not name: continue
                s.add(BoatLog(section_id=sid, name=name, arrival=self.tbl_boats.item(r,1).text().strip(), departure=self.tbl_boats.item(r,2).text().strip(), status=(self.tbl_boats.item(r,3).text().strip() if self.tbl_boats.item(r,3) else "")))
            for r in range(self.tbl_choppers.rowCount()):
                name = self.tbl_choppers.item(r,0).text().strip() if self.tbl_choppers.item(r,0) else ''
                if not name: continue
                pax = None
                try: pax = int(float(self.tbl_choppers.item(r,3).text()))
                except: pax = None
                s.add(ChopperLog(section_id=sid, name=name, arrival=self.tbl_choppers.item(r,1).text().strip(), departure=self.tbl_choppers.item(r,2).text().strip(), pax_in=pax))
        QMessageBox.information(self, "Saved", "Boat & chopper logs saved.")

class BoatsChopperModule(BaseModule):
    DISPLAY_NAME = "Boats & Chopper Log"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = BoatsChopperWidget(self.db)
    def get_widget(self): return self.widget
