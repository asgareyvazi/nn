# File: modules/export_center.py
# Purpose: Export selected Well/Section/date range to CSV (basic) and placeholder for PDF/Excel.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QFileDialog, QMessageBox
from .base import BaseModule
from models import Section, DailyReport, TimeLog
import csv, os
from datetime import datetime

class ExportCenterWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.btn_csv = QPushButton("Export TimeLogs to CSV"); self.btn_pdf = QPushButton("Export PDF (placeholder)")
        self.l.addWidget(self.btn_csv); self.l.addWidget(self.btn_pdf)
        self.btn_csv.clicked.connect(self._export_csv); self.btn_pdf.clicked.connect(self._export_pdf)
        self._load_sections()

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _export_csv(self):
        sid = self.cb_section.currentData()
        if sid is None: return QMessageBox.warning(self, "Select", "Select section first")
        fname, _ = QFileDialog.getSaveFileName(self, "Save CSV", "timelogs.csv", "CSV Files (*.csv)")
        if not fname: return
        with self.db.get_session() as s:
            # Gather all timelogs for section (via DailyReport)
            reports = s.query(DailyReport).filter_by(section_id=sid).all()
            rows = []
            for r in reports:
                for tl in r.timelogs:
                    rows.append({
                        "report_id": r.id, "report_date": r.report_date.isoformat() if r.report_date else "",
                        "from": tl.from_time, "to": tl.to_time, "duration_min": tl.duration_minutes,
                        "main_code": tl.main_code.code if tl.main_code else "", "sub_code": tl.sub_code.code if tl.sub_code else "", "desc": tl.description, "is_npt": tl.is_npt
                    })
        # write csv
        keys = ["report_id","report_date","from","to","duration_min","main_code","sub_code","desc","is_npt"]
        with open(fname, "w", newline='', encoding="utf-8") as f:
            w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(rows)
        QMessageBox.information(self, "Exported", f"Exported {len(rows)} rows to {fname}")

    def _export_pdf(self):
        # placeholder: user can integrate ReportLab here; for now we export CSV and notify
        QMessageBox.information(self, "PDF", "PDF export is a placeholder. CSV export is available. Integrate ReportLab/fpdf for formatted PDF.")

class ExportCenterModule(BaseModule):
    DISPLAY_NAME = "Export Center"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = ExportCenterWidget(self.db)
    def get_widget(self): return self.widget
