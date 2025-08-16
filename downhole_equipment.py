# File: modules/downhole_equipment.py
# Purpose: Downhole equipment CRUD with cumulative counters.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, DownholeEquipment

class DownholeEquipmentWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build()
        self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.tbl = QTableWidget(0, 7); self.tbl.setHorizontalHeaderLabels(["Name","S/N","ID","Sliding Hrs","Cum Rot","Cum Pump","Cum Total Hrs"])
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
        for c in range(7): self.tbl.setItem(r,c, QTableWidgetItem(""))

    def _del(self):
        for r in sorted([i.row() for i in self.tbl.selectionModel().selectedRows()], reverse=True): self.tbl.removeRow(r)

    def _load(self):
        sid = self.cb_section.currentData()
        self.tbl.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            rows = s.query(DownholeEquipment).filter_by(section_id=sid).all()
        for e in rows:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r,0,QTableWidgetItem(e.name or "")); self.tbl.setItem(r,1,QTableWidgetItem(e.sn or ""))
            self.tbl.setItem(r,2,QTableWidgetItem(str(e.inner_id_in or ""))); self.tbl.setItem(r,3,QTableWidgetItem(str(e.sliding_hours or "")))
            self.tbl.setItem(r,4,QTableWidgetItem(str(e.cum_rotation or ""))); self.tbl.setItem(r,5,QTableWidgetItem(str(e.cum_pumping or "")))
            self.tbl.setItem(r,6,QTableWidgetItem(str(e.cum_total_hours or "")))

    def _save(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            for r in s.query(DownholeEquipment).filter_by(section_id=sid).all(): s.delete(r)
            for r in range(self.tbl.rowCount()):
                name = self.tbl.item(r,0).text().strip() if self.tbl.item(r,0) else ''
                if not name: continue
                def f(c):
                    try: return float(self.tbl.item(r,c).text())
                    except: return 0.0
                s.add(DownholeEquipment(
                    section_id=sid, name=name, sn=(self.tbl.item(r,1).text() if self.tbl.item(r,1) else ''),
                    inner_id_in=f(2), sliding_hours=f(3), cum_rotation=f(4), cum_pumping=f(5), cum_total_hours=f(6)
                ))
        QMessageBox.information(self, "Saved", "Downhole equipment saved.")

class DownholeEquipmentModule(BaseModule):
    DISPLAY_NAME = "Downhole Equipment"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = DownholeEquipmentWidget(self.db)
    def get_widget(self): return self.widget
