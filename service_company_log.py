# File: modules/service_company_log.py
# Purpose: Service companies start/end with description per section.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QMessageBox
from .base import BaseModule
from models import Section, ServiceCompanyLog if False else None  # placeholder if separate model absent

# We'll persist via a lightweight per-session CSV because ORM doesn't include a dedicated model.
# If you prefer ORM, add a ServiceCompany model in models.py.

class ServiceCompanyLogWidget(QWidget):
    HEADERS = ["Company Name","Service Type","Start (YYYY-MM-DD HH:mm)","End (YYYY-MM-DD HH:mm)","Description"]
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        v = QVBoxLayout(self)
        self.cb_section=QComboBox(); v.addWidget(self.cb_section)
        self.tbl = QTableWidget(0, len(self.HEADERS)); self.tbl.setHorizontalHeaderLabels(self.HEADERS); v.addWidget(self.tbl)
        h = QHBoxLayout(); self.btn_add=QPushButton("Add"); self.btn_del=QPushButton("Delete"); self.btn_export=QPushButton("Export CSV")
        for b in (self.btn_add,self.btn_del,self.btn_export): h.addWidget(b); v.addLayout(h)
        self.btn_add.clicked.connect(self._add); self.btn_del.clicked.connect(self._del); self.btn_export.clicked.connect(self._export)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        for c in range(self.tbl.columnCount()): self.tbl.setItem(r,c,QTableWidgetItem(""))

    def _del(self):
        for r in sorted([i.row() for i in self.tbl.selectionModel().selectedRows()], reverse=True): self.tbl.removeRow(r)

    def _export(self):
        import csv, os
        sid = self.cb_section.currentData() or 0
        path = f"service_company_log_section_{sid}.csv"
        with open(path, "w", newline='', encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(self.HEADERS)
            for r in range(self.tbl.rowCount()):
                row=[]
                for c in range(self.tbl.columnCount()):
                    it = self.tbl.item(r,c); row.append(it.text() if it else "")
                w.writerow(row)
        QMessageBox.information(self, "Exported", f"Saved to {os.path.abspath(path)}")

class ServiceCompanyLogModule(BaseModule):
    DISPLAY_NAME = "Service Company Log"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = ServiceCompanyLogWidget(self.db)
    def get_widget(self): return self.widget
