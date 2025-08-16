# File: modules/time_breakdown.py
# Purpose: Summarize time per code for a section (aggregator) and manual adjustments.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, TimeBreakdown, TimeLog
from sqlalchemy import func

class TimeBreakdownWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.tbl = QTableWidget(0,3); self.tbl.setHorizontalHeaderLabels(["Code","Total Minutes","Summary"])
        self.l.addWidget(self.tbl)
        h = QHBoxLayout(); self.btn_agg = QPushButton("Aggregate from TimeLogs"); self.btn_save = QPushButton("Save"); h.addWidget(self.btn_agg); h.addWidget(self.btn_save); self.l.addLayout(h)
        self.btn_agg.clicked.connect(self._aggregate); self.btn_save.clicked.connect(self._save)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _load(self):
        self.tbl.setRowCount(0)

    def _aggregate(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        # aggregate by main_code
        with self.db.get_session() as s:
            q = s.query(TimeLog.main_phase_code_id, func.sum(TimeLog.duration_minutes)).join(TimeLog.daily_report).filter(TimeLog.daily_report.has(section_id=sid)).group_by(TimeLog.main_phase_code_id).all()
        self.tbl.setRowCount(0)
        for code_id, minutes in q:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r,0,QTableWidgetItem(str(code_id or '')))
            self.tbl.setItem(r,1,QTableWidgetItem(str(int(minutes or 0))))
            self.tbl.setItem(r,2,QTableWidgetItem(""))
        QMessageBox.information(self, "Aggregated", "Time aggregated by main codes.")

    def _save(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            for rec in s.query(TimeBreakdown).filter_by(section_id=sid).all(): s.delete(rec)
            for r in range(self.tbl.rowCount()):
                code = self.tbl.item(r,0).text().strip() if self.tbl.item(r,0) else ''
                if not code: continue
                try: minutes = int(self.tbl.item(r,1).text())
                except: minutes = 0
                summary = self.tbl.item(r,2).text() if self.tbl.item(r,2) else ''
                s.add(TimeBreakdown(section_id=sid, code=code, total_minutes=minutes, summary=summary))
        QMessageBox.information(self, "Saved", "Time breakdown saved.")

class TimeBreakdownModule(BaseModule):
    DISPLAY_NAME = "Time Breakdown"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = TimeBreakdownWidget(self.db)
    def get_widget(self): return self.widget
