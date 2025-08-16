# File: modules/drill_pipe_specs.py
# Purpose: Drill pipe specs list per section.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, DrillPipeSpec

class DrillPipeSpecsWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.tbl = QTableWidget(0,6); self.tbl.setHorizontalHeaderLabels(["Size & Weight","Connection","ID","Grade","TJ OD/ID","Std No in Derrick"])
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
        for c in range(6): self.tbl.setItem(r,c,QTableWidgetItem(""))

    def _del(self):
        for r in sorted([i.row() for i in self.tbl.selectionModel().selectedRows()], reverse=True): self.tbl.removeRow(r)

    def _load(self):
        sid = self.cb_section.currentData(); self.tbl.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            rows = s.query(DrillPipeSpec).filter_by(section_id=sid).all()
        for rec in rows:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r,0,QTableWidgetItem(rec.size_weight or "")); self.tbl.setItem(r,1,QTableWidgetItem(rec.connection or ""))
            self.tbl.setItem(r,2,QTableWidgetItem(str(rec.inner_d_in or ""))); self.tbl.setItem(r,3,QTableWidgetItem(rec.grade or ""))
            self.tbl.setItem(r,4,QTableWidgetItem(str(rec.tj_od or "") + "/" + str(rec.tj_id or ""))); self.tbl.setItem(r,5,QTableWidgetItem(str(rec.std_no_in_derrick or "")))

    def _save(self):
        sid = self.cb_section.currentData(); 
        if sid is None: return
        with self.db.get_session() as s:
            for rec in s.query(DrillPipeSpec).filter_by(section_id=sid).all(): s.delete(rec)
            for r in range(self.tbl.rowCount()):
                name = self.tbl.item(r,0).text().strip() if self.tbl.item(r,0) else ''
                if not name: continue
                def f(c):
                    try: return float(self.tbl.item(r,c).text())
                    except: return None
                s.add(DrillPipeSpec(section_id=sid, size_weight=name, connection=(self.tbl.item(r,1).text() if self.tbl.item(r,1) else ''), id_in=f(2), grade=(self.tbl.item(r,3).text() if self.tbl.item(r,3) else ''), tj_od=f(4), tj_id=None, std_no_in_derrick=int(float(self.tbl.item(r,5).text())) if self.tbl.item(r,5) else None))
        QMessageBox.information(self, "Saved", "Drill pipe specs saved.")

class DrillPipeSpecsModule(BaseModule):
    DISPLAY_NAME = "Drill Pipe Specs"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = DrillPipeSpecsWidget(self.db)
    def get_widget(self): return self.widget
