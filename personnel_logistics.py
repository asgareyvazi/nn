# File: modules/personnel_logistics.py
# Purpose: Crew list + arrivals/departures, fuel/water used, transport notes.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QTextEdit, QFormLayout, QDoubleSpinBox, QMessageBox
from .base import BaseModule
from models import Section, Crew

class PersonnelLogisticsWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        v = QVBoxLayout(self)
        self.cb_section=QComboBox(); v.addWidget(self.cb_section)

        # Crew
        self.tbl_crew = QTableWidget(0,4); self.tbl_crew.setHorizontalHeaderLabels(["Company","Service","No.","Date IN (YYYY-MM-DD)"])
        h1 = QHBoxLayout(); self.btn_add=QPushButton("Add Crew"); self.btn_del=QPushButton("Delete Selected")
        h1.addWidget(self.btn_add); h1.addWidget(self.btn_del)
        v.addLayout(h1); v.addWidget(self.tbl_crew)
        self.btn_add.clicked.connect(lambda: self._add_row(self.tbl_crew, 4)); self.btn_del.clicked.connect(lambda: self._del_row(self.tbl_crew))

        # Logistics
        frm = QFormLayout()
        self.fuel_used=QDoubleSpinBox(); self.water_used=QDoubleSpinBox()
        self.fuel_used.setRange(0,1e6); self.water_used.setRange(0,1e6); self.fuel_used.setDecimals(2); self.water_used.setDecimals(2)
        self.txt_transport = QTextEdit()
        frm.addRow("Fuel Used", self.fuel_used); frm.addRow("Water Used", self.water_used); frm.addRow("Transport Notes", self.txt_transport)
        v.addLayout(frm)

        # Save
        h2 = QHBoxLayout(); self.btn_save = QPushButton("Save"); h2.addWidget(self.btn_save); v.addLayout(h2)
        self.btn_save.clicked.connect(self._save)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _add_row(self, tbl, cols):
        r = tbl.rowCount(); tbl.insertRow(r)
        for c in range(cols): tbl.setItem(r,c,QTableWidgetItem(""))

    def _del_row(self, tbl):
        for r in sorted([i.row() for i in tbl.selectionModel().selectedRows()], reverse=True): tbl.removeRow(r)

    def _load(self):
        sid = self.cb_section.currentData()
        self.tbl_crew.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            rows = s.query(Crew).filter_by(section_id=sid).all()
        for c in rows:
            r = self.tbl_crew.rowCount(); self.tbl_crew.insertRow(r)
            self.tbl_crew.setItem(r,0,QTableWidgetItem(c.company or "")); self.tbl_crew.setItem(r,1,QTableWidgetItem(c.service or ""))
            self.tbl_crew.setItem(r,2,QTableWidgetItem(str(c.count or 0))); self.tbl_crew.setItem(r,3,QTableWidgetItem(str(c.date_in or "")))

    def _save(self):
        sid = self.cb_section.currentData(); if sid is None: return
        with self.db.get_session() as s:
            for c in s.query(Crew).filter_by(section_id=sid).all(): s.delete(c)
            for r in range(self.tbl_crew.rowCount()):
                company = self.tbl_crew.item(r,0).text().strip() if self.tbl_crew.item(r,0) else ''
                service = self.tbl_crew.item(r,1).text().strip() if self.tbl_crew.item(r,1) else ''
                if not company and not service: continue
                def n(c):
                    try: return int(float(self.tbl_crew.item(r,c).text()))
                    except: return 0
                s.add(Crew(section_id=sid, company=company, service=service, count=n(2)))
        QMessageBox.information(self, "Saved", "Personnel & logistics saved.")

class PersonnelLogisticsModule(BaseModule):
    DISPLAY_NAME = "Personnel & Logistics"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = PersonnelLogisticsWidget(self.db)
    def get_widget(self): return self.widget
