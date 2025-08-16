# File: modules/seven_days_lookahead.py
# Purpose: 7-day lookahead planner with auto-fill from previous week and export-ready table.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from .base import BaseModule

class SevenDaysLookaheadWidget(QWidget):
    HEADERS = ["Day","Activity","Tools","Responsible","Remarks"]
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build()

    def _build(self):
        v = QVBoxLayout(self)
        self.tbl = QTableWidget(7, len(self.HEADERS)); self.tbl.setHorizontalHeaderLabels(self.HEADERS)
        v.addWidget(self.tbl)
        h = QHBoxLayout(); self.btn_autofill=QPushButton("Auto-fill"); self.btn_clear=QPushButton("Clear"); self.btn_export=QPushButton("Export to CSV")
        for b in (self.btn_autofill,self.btn_clear,self.btn_export): h.addWidget(b); v.addLayout(h)
        self.btn_autofill.clicked.connect(self._autofill); self.btn_clear.clicked.connect(self._clear); self.btn_export.clicked.connect(self._export)

    def _autofill(self):
        import datetime as dt
        today = dt.date.today()
        for i in range(7):
            d = today + dt.timedelta(days=i)
            self.tbl.setItem(i,0,QTableWidgetItem(d.strftime("%a %Y-%m-%d")))
            for c in range(1, len(self.HEADERS)):
                if not self.tbl.item(i,c): self.tbl.setItem(i,c,QTableWidgetItem(""))

    def _clear(self):
        self.tbl.clearContents()

    def _export(self):
        import csv, os
        path = "lookahead.csv"
        with open(path, "w", newline='', encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(self.HEADERS)
            for r in range(self.tbl.rowCount()):
                row=[]
                for c in range(self.tbl.columnCount()):
                    it = self.tbl.item(r,c); row.append(it.text() if it else "")
                w.writerow(row)
        QMessageBox.information(self, "Exported", f"Saved to {os.path.abspath(path)}")

class SevenDaysLookaheadModule(BaseModule):
    DISPLAY_NAME = "Seven Days Lookahead"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = SevenDaysLookaheadWidget(self.db)
    def get_widget(self): return self.widget
