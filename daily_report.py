
# =========================================
# file: nikan_drill_master/modules/daily_report.py
# =========================================
from __future__ import annotations
from datetime import date
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QTimeEdit, QCheckBox, QComboBox, QMessageBox
from PySide6.QtCore import QTime
from sqlalchemy.orm import Session
from database import session_scope
from modules.base import ModuleBase
from models import Section, DailyReport, TimeLog, CodeMain, CodeSub
from utils import minutes_between

class DailyReportModule(ModuleBase):
    COL_FROM, COL_TO, COL_DUR, COL_MAIN, COL_SUB, COL_DESC, COL_NPT, COL_STATUS = range(8)

    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._section_id: int | None = None
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.report_date = QDateEdit(); self.report_date.setCalendarPopup(True)
        self.rig_day = QSpinBox(); self.rig_day.setRange(0, 10000)
        self.depth_0000 = QSpinBox(); self.depth_0000.setRange(0, 100000)
        self.depth_0600 = QSpinBox(); self.depth_0600.setRange(0, 100000)
        self.depth_2400 = QSpinBox(); self.depth_2400.setRange(0, 100000)
        self.pit_gain = QDoubleSpinBox(); self.pit_gain.setDecimals(2); self.pit_gain.setRange(-1e6, 1e6)

        self.operations_done = QTextEdit()
        self.work_summary = QTextEdit()
        self.alerts = QTextEdit()
        self.general_notes = QTextEdit()

        form.addRow("Report Date", self.report_date)
        form.addRow("Rig Day", self.rig_day)
        form.addRow("Depth @ 00:00 / 06:00 / 24:00", _row3(self.depth_0000, self.depth_0600, self.depth_2400))
        form.addRow("Pit Gain", self.pit_gain)
        form.addRow("Operations Done", self.operations_done)
        form.addRow("Work Summary", self.work_summary)
        form.addRow("Alerts/Problems", self.alerts)
        form.addRow("General Notes", self.general_notes)

        # Time Log
        self.tbl = QTableWidget(0, 8)
        self.tbl.setHorizontalHeaderLabels(["From", "To", "Duration (min)", "Main Code", "Sub-Code", "Description", "NPT", "Status"])

        btns = QHBoxLayout()
        add = QPushButton("Add Row"); delete = QPushButton("Delete Row"); save = QPushButton("Save")
        add.clicked.connect(self._add_row); delete.clicked.connect(self._del_row); save.clicked.connect(self._save)
        btns.addWidget(add); btns.addWidget(delete); btns.addStretch(1); btns.addWidget(save)

        lay.addLayout(form)
        lay.addLayout(btns)
        lay.addWidget(self.tbl)

    def on_activated(self, context: dict) -> None:
        self.on_selection_changed(context)

    def on_selection_changed(self, context: dict) -> None:
        sel = context.get("selection")
        if sel and sel[0] == "section":
            self._section_id = int(sel[1])
        # در این نسخه: ایجاد گزارش جدید با تاریخ انتخابی کاربر

    def _add_row(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        from_edit = QTimeEdit(); to_edit = QTimeEdit()
        from_edit.setTime(QTime(0,0)); to_edit.setTime(QTime(0,0))
        self.tbl.setCellWidget(r, self.COL_FROM, from_edit)
        self.tbl.setCellWidget(r, self.COL_TO, to_edit)
        self.tbl.setItem(r, self.COL_DUR, QTableWidgetItem("0"))

        main_cb = QComboBox(); main_cb.addItem("", None)
        sub_cb = QComboBox(); sub_cb.addItem("", None)
        with session_scope(self.SessionLocal) as s:
            mains = s.query(CodeMain).order_by(CodeMain.phase, CodeMain.code).all()
            for m in mains:
                main_cb.addItem(f"{m.phase}-{m.code}-{m.name}", m.id)
        main_cb.currentIndexChanged.connect(lambda _=None, row=r: self._reload_subcodes(row))
        self.tbl.setCellWidget(r, self.COL_MAIN, main_cb)
        self.tbl.setCellWidget(r, self.COL_SUB, sub_cb)

        self.tbl.setItem(r, self.COL_DESC, QTableWidgetItem(""))
        chk = QCheckBox()
        self.tbl.setCellWidget(r, self.COL_NPT, chk)
        status = QComboBox(); status.addItems(["", "Done", "Continue", "Pending"])
        self.tbl.setCellWidget(r, self.COL_STATUS, status)

        from_edit.timeChanged.connect(lambda _=None, row=r: self._recalc_duration(row))
        to_edit.timeChanged.connect(lambda _=None, row=r: self._recalc_duration(row))

    def _reload_subcodes(self, row: int):
        main_cb: QComboBox = self.tbl.cellWidget(row, self.COL_MAIN)  # type: ignore
        sub_cb: QComboBox = self.tbl.cellWidget(row, self.COL_SUB)   # type: ignore
        sub_cb.clear(); sub_cb.addItem("", None)
        main_id = main_cb.currentData()
        if not main_id:
            return
        with session_scope(self.SessionLocal) as s:
            subs = s.query(CodeSub).filter(CodeSub.main_id == main_id).order_by(CodeSub.sub_code).all()
            for x in subs:
                sub_cb.addItem(f"{x.sub_code}-{x.name}", x.id)

    def _recalc_duration(self, row: int):
        fe: QTimeEdit = self.tbl.cellWidget(row, self.COL_FROM)  # type: ignore
        te: QTimeEdit = self.tbl.cellWidget(row, self.COL_TO)    # type: ignore
        mins = minutes_between(fe.time().toPython(), te.time().toPython())
        self.tbl.item(row, self.COL_DUR).setText(str(mins))

    def _del_row(self):
        r = self.tbl.currentRow()
        if r >= 0:
            self.tbl.removeRow(r)

    def _save(self):
        if not self._section_id:
            QMessageBox.warning(self, "Selection", "ابتدا درخت سمت چپ: Section را انتخاب کنید")
            return
        dr_date = self.report_date.date().toPython()
        with session_scope(self.SessionLocal) as s:
            dr = s.query(DailyReport).filter(DailyReport.section_id==self._section_id, DailyReport.report_date==dr_date).one_or_none()
            if not dr:
                dr = DailyReport(section_id=self._section_id, report_date=dr_date)
                s.add(dr); s.flush()

            dr.rig_day = self.rig_day.value()
            dr.depth_0000_ft = self.depth_0000.value()
            dr.depth_0600_ft = self.depth_0600.value()
            dr.depth_2400_ft = self.depth_2400.value()
            dr.pit_gain = self.pit_gain.value()
            dr.operations_done = self.operations_done.toPlainText().strip() or None
            dr.work_summary = self.work_summary.toPlainText().strip() or None
            dr.alerts = self.alerts.toPlainText().strip() or None
            dr.general_notes = self.general_notes.toPlainText().strip() or None

            # clear and re-add time logs
            s.query(TimeLog).filter(TimeLog.daily_report_id==dr.id).delete()
            s.flush()
            for r in range(self.tbl.rowCount()):
                fe: QTimeEdit = self.tbl.cellWidget(r, self.COL_FROM)  # type: ignore
                te: QTimeEdit = self.tbl.cellWidget(r, self.COL_TO)    # type: ignore
                dur = int(self.tbl.item(r, self.COL_DUR).text()) if self.tbl.item(r, self.COL_DUR) else 0
                main_id = self.tbl.cellWidget(r, self.COL_MAIN).currentData()  # type: ignore
                sub_id = self.tbl.cellWidget(r, self.COL_SUB).currentData()    # type: ignore
                desc = self.tbl.item(r, self.COL_DESC).text() if self.tbl.item(r, self.COL_DESC) else ""
                is_npt = bool(self.tbl.cellWidget(r, self.COL_NPT).isChecked())  # type: ignore
                status = self.tbl.cellWidget(r, self.COL_STATUS).currentText()   # type: ignore

                s.add(TimeLog(
                    daily_report_id=dr.id,
                    time_from=fe.time().toPython(),
                    time_to=te.time().toPython(),
                    duration_min=dur,
                    main_code_id=main_id,
                    sub_code_id=sub_id,
                    description=desc or None,
                    is_npt=is_npt,
                    status=status or None
                ))
        QMessageBox.information(self, "Saved", "Daily Report ذخیره شد")

def _row3(a, b, c):
    w = QWidget(); from PySide6.QtWidgets import QHBoxLayout
    lay = QHBoxLayout(w); lay.setContentsMargins(0,0,0,0); lay.addWidget(a); lay.addWidget(b); lay.addWidget(c)
    return w
