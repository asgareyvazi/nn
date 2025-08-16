# File: modules/inventory.py
# Purpose: Inventory CRUD with add/remove rows and dynamic unit.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QMessageBox
from .base import BaseModule
from models import Section, InventoryItem

class InventoryWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        v = QVBoxLayout(self)
        self.cb_section=QComboBox(); v.addWidget(self.cb_section)
        self.tbl = QTableWidget(0,6); self.tbl.setHorizontalHeaderLabels(["Item","Opening","Received","Used","Remaining","Unit"])
        v.addWidget(self.tbl)
        h = QHBoxLayout(); self.btn_add=QPushButton("Add Row"); self.btn_del=QPushButton("Delete Selected"); self.btn_save=QPushButton("Save")
        for b in (self.btn_add,self.btn_del,self.btn_save): h.addWidget(b); v.addLayout(h)
        self.btn_add.clicked.connect(self._add_row); self.btn_del.clicked.connect(self._del_row); self.btn_save.clicked.connect(self._save)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _add_row(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        for c in range(6): self.tbl.setItem(r, c, QTableWidgetItem(""))

    def _del_row(self):
        sel = self.tbl.selectionModel().selectedRows()
        for r in sorted([i.row() for i in sel], reverse=True): self.tbl.removeRow(r)

    def _load(self):
        sid = self.cb_section.currentData()
        self.tbl.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            items = s.query(InventoryItem).filter_by(section_id=sid).all()
        for it in items:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r,0,QTableWidgetItem(it.item or "")); self.tbl.setItem(r,1,QTableWidgetItem(str(it.opening or 0)))
            self.tbl.setItem(r,2,QTableWidgetItem(str(it.received or 0))); self.tbl.setItem(r,3,QTableWidgetItem(str(it.used or 0)))
            self.tbl.setItem(r,4,QTableWidgetItem(str(it.remaining or 0))); self.tbl.setItem(r,5,QTableWidgetItem(it.unit or ""))

    def _save(self):
        sid = self.cb_section.currentData(); if sid is None: return
        with self.db.get_session() as s:
            # clear and recreate
            for it in s.query(InventoryItem).filter_by(section_id=sid).all(): s.delete(it)
            for r in range(self.tbl.rowCount()):
                name = self.tbl.item(r,0).text().strip() if self.tbl.item(r,0) else ''
                if not name: continue
                def f(c):
                    try: return float(self.tbl.item(r,c).text())
                    except: return 0.0
                s.add(InventoryItem(
                    section_id=sid, item=name,
                    opening=f(1), received=f(2), used=f(3), remaining=f(4),
                    unit=(self.tbl.item(r,5).text().strip() if self.tbl.item(r,5) else '')
                ))
        QMessageBox.information(self, "Saved", "Inventory saved.")

class InventoryModule(BaseModule):
    DISPLAY_NAME = "Inventory"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = InventoryWidget(self.db)
    def get_widget(self): return self.widget
