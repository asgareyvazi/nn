from __future__ import annotations
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QTableWidgetItem, QMessageBox, QDateTimeEdit
from modules.base import ModuleBase
from database import session_scope
from models import ServiceCompanyLog, DailyReport

class ServiceCompanyLogModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels(["Company Name","Service Type","Start","End","Description"])
        btns = QHBoxLayout()
        add = QPushButton("Add"); rm = QPushButton("Delete"); save = QPushButton("Save (latest DR)")
        add.clicked.connect(self._add); rm.clicked.connect(lambda: self.tbl.removeRow(self.tbl.currentRow())); save.clicked.connect(self._save)
        btns.addWidget(add); btns.addWidget(rm); btns.addStretch(1); btns.addWidget(save)
        lay.addLayout(btns); lay.addWidget(self.tbl)

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        self.tbl.setItem(r,0, QTableWidgetItem(""))
        self.tbl.setItem(r,1, QTableWidgetItem(""))
        sdt, edt = QDateTimeEdit(), QDateTimeEdit()
        sdt.setCalendarPopup(True); edt.setCalendarPopup(True)
        self.tbl.setCellWidget(r,2,sdt); self.tbl.setCellWidget(r,3,edt)
        self.tbl.setItem(r,4, QTableWidgetItem(""))

    def _save(self):
        with session_scope(self.SessionLocal) as s:
            dr = s.query(DailyReport).order_by(DailyReport.report_date.desc()).first()
            if not dr:
                QMessageBox.warning(self, "No DR", "ابتدا Daily Report بسازید")
                return
            s.query(ServiceCompanyLog).filter(ServiceCompanyLog.daily_report_id==dr.id).delete()
            s.flush()
            for r in range(self.tbl.rowCount()):
                name = self.tbl.item(r,0).text() if self.tbl.item(r,0) else ""
                stw = self.tbl.cellWidget(r,2); etw = self.tbl.cellWidget(r,3)
                start_dt = stw.dateTime().toPython() if isinstance(stw, QDateTimeEdit) else None
                end_dt = etw.dateTime().toPython() if isinstance(etw, QDateTimeEdit) else None
                stype = self.tbl.item(r,1).text() if self.tbl.item(r,1) else ""
                desc = self.tbl.item(r,4).text() if self.tbl.item(r,4) else ""
                if name:
                    s.add(ServiceCompanyLog(
                        daily_report_id=dr.id,
                        company_name=name, service_type=stype or None,
                        start_dt=start_dt, end_dt=end_dt, description=desc or None
                    ))
        QMessageBox.information(self, "Saved", "Service Company Log ذخیره شد")
