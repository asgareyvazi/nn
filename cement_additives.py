# File: modules/cement_additives.py
# Purpose: Cement & Additives inventory per section.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, CementInventory

class CementAdditivesWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build()
        self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.tbl = QTableWidget(0,5); self.tbl.setHorizontalHeaderLabels(["Material","Received","Consumed","Backload","Last Inventory"])
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
        for c in range(5): self.tbl.setItem(r,c,QTableWidgetItem(""))

    def _del(self):
        for r in sorted([i.row() for i in self.tbl.selectionModel().selectedRows()], reverse=True): self.tbl.removeRow(r)

    def _load(self):
        sid = self.cb_section.currentData(); self.tbl.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            rows = s.query(CementInventory).filter_by(section_id=sid).all()
        for rec in rows:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r,0,QTableWidgetItem(rec.material or "")); self.tbl.setItem(r,1,QTableWidgetItem(str(rec.received or 0)))
            self.tbl.setItem(r,2,QTableWidgetItem(str(rec.consumed or 0))); self.tbl.setItem(r,3,QTableWidgetItem(str(rec.backload or 0)))
            self.tbl.setItem(r,4,QTableWidgetItem(str(rec.last_inventory or 0)))

    def _save(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            for rec in s.query(CementInventory).filter_by(section_id=sid).all(): s.delete(rec)
            for r in range(self.tbl.rowCount()):
                mat = self.tbl.item(r,0).text().strip() if self.tbl.item(r,0) else ''
                if not mat: continue
                def f(c):
                    try: return float(self.tbl.item(r,c).text())
                    except: return 0.0
                s.add(CementInventory(section_id=sid, material=mat, received=f(1), consumed=f(2), backload=f(3), last_inventory=f(4)))
        QMessageBox.information(self, "Saved", "Cement & additives saved.")

class CementAdditivesModule(BaseModule):
    DISPLAY_NAME = "Cement & Additives"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = CementAdditivesWidget(self.db)
    def get_widget(self): return self.widget
