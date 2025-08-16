# File: modules/formation_data.py
# Purpose: Formation tops and formation data management per section.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, FormationTop, FormationTopData

class FormationDataWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.tbl_tops = QTableWidget(0,3); self.tbl_tops.setHorizontalHeaderLabels(["Name","Lithology","Top MD"])
        self.tbl_data = QTableWidget(0,4); self.tbl_data.setHorizontalHeaderLabels(["Name","MD","TVD","Lithology"])
        self.l.addWidget(self.tbl_tops); self.l.addWidget(self.tbl_data)
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
        self.tbl_tops.insertRow(self.tbl_tops.rowCount()); self.tbl_data.insertRow(self.tbl_data.rowCount())

    def _del(self):
        for tbl in (self.tbl_tops, self.tbl_data):
            for r in sorted([i.row() for i in tbl.selectionModel().selectedRows()], reverse=True):
                tbl.removeRow(r)

    def _load(self):
        sid = self.cb_section.currentData()
        self.tbl_tops.setRowCount(0); self.tbl_data.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            tops = s.query(FormationTop).filter_by(section_id=sid).all()
            data = s.query(FormationTopData).filter_by(section_id=sid).all()
        for t in tops:
            r = self.tbl_tops.rowCount(); self.tbl_tops.insertRow(r)
            self.tbl_tops.setItem(r,0,QTableWidgetItem(t.name or "")); self.tbl_tops.setItem(r,1,QTableWidgetItem(t.lithology or "")); self.tbl_tops.setItem(r,2,QTableWidgetItem(str(t.top_md or "")))
        for d in data:
            r = self.tbl_data.rowCount(); self.tbl_data.insertRow(r)
            self.tbl_data.setItem(r,0,QTableWidgetItem(d.name or "")); self.tbl_data.setItem(r,1,QTableWidgetItem(str(d.md or ""))); self.tbl_data.setItem(r,2,QTableWidgetItem(str(d.tvd or ""))); self.tbl_data.setItem(r,3,QTableWidgetItem(d.lithology or ""))

    def _save(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            for x in s.query(FormationTop).filter_by(section_id=sid).all(): s.delete(x)
            for x in s.query(FormationTopData).filter_by(section_id=sid).all(): s.delete(x)
            for r in range(self.tbl_tops.rowCount()):
                name = self.tbl_tops.item(r,0).text().strip() if self.tbl_tops.item(r,0) else ''
                if not name: continue
                def f(c):
                    try: return float(self.tbl_tops.item(r,c).text())
                    except: return None
                s.add(FormationTop(section_id=sid, name=name, lithology=(self.tbl_tops.item(r,1).text() if self.tbl_tops.item(r,1) else ''), top_md=f(2)))
            for r in range(self.tbl_data.rowCount()):
                name = self.tbl_data.item(r,0).text().strip() if self.tbl_data.item(r,0) else ''
                if not name: continue
                def f(c):
                    try: return float(self.tbl_data.item(r,c).text())
                    except: return None
                s.add(FormationTopData(section_id=sid, name=name, md=f(1), tvd=f(2), lithology=(self.tbl_data.item(r,3).text() if self.tbl_data.item(r,3) else '')))
        QMessageBox.information(self, "Saved", "Formation data saved.")

class FormationDataModule(BaseModule):
    DISPLAY_NAME = "Formation Data"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = FormationDataWidget(self.db)
    def get_widget(self): return self.widget
