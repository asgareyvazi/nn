from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QTableWidgetItem, QFileDialog, QMessageBox, QComboBox, QDateEdit, QFormLayout
from modules.base import ModuleBase
from database import session_scope
from models import Well, Section, DailyReport, TimeLog, CodeMain
from utils import export_table_to_csv

class TimeBreakdownModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.cb_well = QComboBox(); self.cb_section = QComboBox()
        self.dt_from = QDateEdit(); self.dt_from.setCalendarPopup(True)
        self.dt_to = QDateEdit(); self.dt_to.setCalendarPopup(True)
        form.addRow("Well", self.cb_well); form.addRow("Section", self.cb_section)
        form.addRow("From", self.dt_from); form.addRow("To", self.dt_to)
        self.tbl = QTableWidget(0, 4)
        self.tbl.setHorizontalHeaderLabels(["Phase","Main Code","Total Minutes","Total Hours"])
        btns = QHBoxLayout()
        refresh = QPushButton("Calculate"); export = QPushButton("Export CSV")
        refresh.clicked.connect(self._calc); export.clicked.connect(self._export)
        btns.addWidget(refresh); btns.addStretch(1); btns.addWidget(export)
        lay.addLayout(form); lay.addLayout(btns); lay.addWidget(self.tbl)

    def on_activated(self, context: dict) -> None:
        self._reload()

    def _reload(self):
        self.cb_well.clear(); self.cb_section.clear()
        with session_scope(self.SessionLocal) as s:
            wells = s.query(Well).order_by(Well.name).all()
            for w in wells: self.cb_well.addItem(w.name, w.id)
        self.cb_well.currentIndexChanged.connect(self._reload_sections)
        self._reload_sections()

    def _reload_sections(self):
        self.cb_section.clear()
        wid = self.cb_well.currentData()
        if not wid: return
        with session_scope(self.SessionLocal) as s:
            sections = s.query(Section).filter(Section.well_id==wid).order_by(Section.name).all()
            for sec in sections: self.cb_section.addItem(sec.name, sec.id)

    def _calc(self):
        sec_id = self.cb_section.currentData()
        if not sec_id: return
        data = defaultdict(int)  # key: (phase, code) -> minutes
        with session_scope(self.SessionLocal) as s:
            q = s.query(DailyReport).filter(DailyReport.section_id==sec_id)
            if self.dt_from.date().isValid():
                q = q.filter(DailyReport.report_date >= self.dt_from.date().toPython())
            if self.dt_to.date().isValid():
                q = q.filter(DailyReport.report_date <= self.dt_to.date().toPython())
            drs = q.all()
            for dr in drs:
                for tl in dr.time_logs:
                    if tl.main_code_id:
                        mc: CodeMain | None = s.get(CodeMain, tl.main_code_id)
                        if mc:
                            data[(mc.phase, mc.code)] += tl.duration_min or 0
        # fill table
        self.tbl.setRowCount(0)
        for (phase, code), mins in sorted(data.items()):
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r,0, QTableWidgetItem(phase))
            self.tbl.setItem(r,1, QTableWidgetItem(code))
            self.tbl.setItem(r,2, QTableWidgetItem(str(mins)))
            self.tbl.setItem(r,3, QTableWidgetItem(f"{mins/60:.2f}"))

    def _export(self):
        out, _ = QFileDialog.getSaveFileName(self, "Export CSV", "time_breakdown.csv", "CSV (*.csv)")
        if not out: return
        headers = ["Phase","Main Code","Total Minutes","Total Hours"]
        rows = []
        for r in range(self.tbl.rowCount()):
            rows.append([self.tbl.item(r,c).text() if self.tbl.item(r,c) else "" for c in range(4)])
        export_table_to_csv(headers, rows, Path(out))
        QMessageBox.information(self, "Export", "CSV ذخیره شد")
