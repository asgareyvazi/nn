# File: modules/survey_data.py
# Purpose: Survey table with add/remove rows (MD, Inc, TVD, Azi, North, East).

from PySide2.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, Survey

class SurveyDataWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.tbl = QTableWidget(0,10); self.tbl.setHorizontalHeaderLabels(["MD","Inc","TVD","Azi","Azimuth","North","East","VS/HD","DLS","Tool"])
        self.l.addWidget(self.tbl)
        h = QHBoxLayout(); self.btn_add = QPushButton("Add"); self.btn_del = QPushButton("Delete"); self.btn_save = QPushButton("Save")
        h.addWidget(self.btn_add); h.addWidget(self.btn_del); h.addWidget(self.btn_save); self.l.addLayout(h)
        self.btn_add.clicked.connect(self._add); self.btn_del.clicked.connect(self._del); self.btn_save.clicked.connect(self._save)
        self.cb_section.currentIndexChanged.connect(self._load)
        self._load_sections()

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        for c in range(10): self.tbl.setItem(r,c,QTableWidgetItem(""))

    def _del(self):
        for r in sorted([i.row() for i in self.tbl.selectionModel().selectedRows()], reverse=True): self.tbl.removeRow(r)

    def _load(self):
        sid = self.cb_section.currentData(); self.tbl.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            rows = s.query(Survey).filter_by(section_id=sid).all()
        for rec in rows:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r,0,QTableWidgetItem(str(rec.md or ""))); self.tbl.setItem(r,1,QTableWidgetItem(str(rec.inc or "")))
            self.tbl.setItem(r,2,QTableWidgetItem(str(rec.tvd or ""))); self.tbl.setItem(r,3,QTableWidgetItem(str(rec.azi or "")))
            self.tbl.setItem(r,4,QTableWidgetItem(str(rec.azimuth or ""))); self.tbl.setItem(r,5,QTableWidgetItem(str(rec.north or "")))
            self.tbl.setItem(r,6,QTableWidgetItem(str(rec.east or ""))); self.tbl.setItem(r,7,QTableWidgetItem(str(rec.vs_hd or "")))
            self.tbl.setItem(r,8,QTableWidgetItem(str(rec.dls or ""))); self.tbl.setItem(r,9,QTableWidgetItem(rec.tool or ""))

    def _save(self):
        sid = self.cb_section.currentData(); 
        if sid is None: return
        with self.db.get_session() as s:
            for rec in s.query(Survey).filter_by(section_id=sid).all(): s.delete(rec)
            for r in range(self.tbl.rowCount()):
                def f(c):
                    try: return float(self.tbl.item(r,c).text())
                    except: return None
                s.add(Survey(section_id=sid, md=f(0), inc=f(1), tvd=f(2), azi=f(3), azimuth=f(4), north=f(5), east=f(6), vs_hd=f(7), dls=f(8), tool=(self.tbl.item(r,9).text() if self.tbl.item(r,9) else "")))
        QMessageBox.information(self, "Saved", "Survey data saved.")

class SurveyDataModule(BaseModule):
    DISPLAY_NAME = "Survey Data"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = SurveyDataWidget(self.db)
    def get_widget(self): return self.widget
