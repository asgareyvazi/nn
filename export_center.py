from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QComboBox, QDateEdit, QPushButton, QFileDialog, QMessageBox
from sqlalchemy.orm import Session
from modules.base import ModuleBase
from database import session_scope
from models import Company, Project, Well, Section, DailyReport, TimeLog
from utils import export_table_to_csv

class ExportCenterModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.cb_well = QComboBox(); self.cb_section = QComboBox()
        self.dt_from = QDateEdit(); self.dt_from.setCalendarPopup(True)
        self.dt_to = QDateEdit(); self.dt_to.setCalendarPopup(True)
        self.cb_format = QComboBox(); self.cb_format.addItems(["CSV", "Excel (.xlsx)", "PDF"])
        btn = QPushButton("Export")
        btn.clicked.connect(self._export)
        form.addRow("Well", self.cb_well); form.addRow("Section", self.cb_section)
        form.addRow("Date From", self.dt_from); form.addRow("Date To", self.dt_to)
        form.addRow("Format", self.cb_format)
        lay.addLayout(form); lay.addWidget(btn)

    def on_activated(self, context: dict) -> None:
        self._reload()

    def _reload(self):
        self.cb_well.clear(); self.cb_section.clear()
        with session_scope(self.SessionLocal) as s:
            wells = s.query(Well).order_by(Well.name).all()
            for w in wells:
                self.cb_well.addItem(w.name, w.id)
        self.cb_well.currentIndexChanged.connect(self._reload_sections)
        self._reload_sections()

    def _reload_sections(self):
        self.cb_section.clear()
        wid = self.cb_well.currentData()
        if not wid: return
        with session_scope(self.SessionLocal) as s:
            sections = s.query(Section).filter(Section.well_id==wid).order_by(Section.name).all()
            for sec in sections:
                self.cb_section.addItem(sec.name, sec.id)

    def _export(self):
        fmt = self.cb_format.currentText()
        sec_id = self.cb_section.currentData()
        if not sec_id:
            QMessageBox.warning(self, "Selection", "Section را انتخاب کنید")
            return
        suffix = ".csv" if fmt=="CSV" else (".xlsx" if fmt.startswith("Excel") else ".pdf")
        out, _ = QFileDialog.getSaveFileName(self, "Export", f"export{suffix}", f"*{suffix}")
        if not out: return
        out_path = Path(out)

        with session_scope(self.SessionLocal) as s:
            q = s.query(DailyReport).filter(DailyReport.section_id==sec_id)
            if self.dt_from.date().isValid():
                q = q.filter(DailyReport.report_date >= self.dt_from.date().toPython())
            if self.dt_to.date().isValid():
                q = q.filter(DailyReport.report_date <= self.dt_to.date().toPython())
            drs = q.order_by(DailyReport.report_date.asc()).all()

            headers = ["ReportDate","RigDay","Depth0000","Depth0600","Depth2400","PitGain","Operations","WorkSummary","Alerts","Notes"]
            rows = []
            for dr in drs:
                rows.append([
                    dr.report_date.isoformat(), dr.rig_day, dr.depth_0000_ft, dr.depth_0600_ft, dr.depth_2400_ft,
                    dr.pit_gain, dr.operations_done or "", dr.work_summary or "", dr.alerts or "", dr.general_notes or ""
                ])

        if fmt=="CSV":
            export_table_to_csv(headers, rows, out_path)
            QMessageBox.information(self, "Export", f"CSV ذخیره شد: {out_path}")
        elif fmt.startswith("Excel"):
            try:
                from openpyxl import Workbook
                wb = Workbook(); ws = wb.active; ws.title = "DailyReports"
                ws.append(headers)
                for r in rows: ws.append(r)
                wb.save(out_path)
                QMessageBox.information(self, "Export", f"XLSX ذخیره شد: {out_path}")
            except Exception as e:
                QMessageBox.warning(self, "Excel", f"نیاز به openpyxl دارید: pip install openpyxl\n{e}")
        else:  # PDF
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                from reportlab.lib.units import cm
                c = canvas.Canvas(str(out_path), pagesize=A4)
                width, height = A4
                x0, y = 2*cm, height-2*cm
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x0, y, "Nikan Drill Master - Daily Reports")
                y -= 0.8*cm
                c.setFont("Helvetica", 8)
                # header
                c.drawString(x0, y, " | ".join(headers))
                y -= 0.5*cm
                for r in rows:
                    line = " | ".join([str(x) if x is not None else "" for x in r])[:180]
                    if y < 2*cm:
                        c.showPage(); y = height-2*cm; c.setFont("Helvetica", 8)
                    c.drawString(x0, y, line)
                    y -= 0.45*cm
                c.showPage(); c.save()
                QMessageBox.information(self, "Export", f"PDF ذخیره شد: {out_path}")
            except Exception as e:
                QMessageBox.warning(self, "PDF", f"نیاز به reportlab دارید: pip install reportlab\n{e}")
