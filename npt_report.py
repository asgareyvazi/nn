from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QTimeEdit, QComboBox, QTextEdit, QLineEdit, QMessageBox
from PySide6.QtCore import QTime
from sqlalchemy.orm import Session
from modules.base import ModuleBase
from database import session_scope
from models import DailyReport, NPTEntry, CodeMain, CodeSub
from utils import minutes_between

class NPTReportModule(ModuleBase):
    COL_FROM, COL_TO, COL_DUR, COL_MAIN, COL_SUB, COL_DESC, COL_RESP = range(7)

    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        self.tbl = QTableWidget(0, 7)
        self.tbl.setHorizontalHeaderLabels(["From","To","Duration(min)","Code","Sub-Code","Description","Responsible"])
        btns = QHBoxLayout()
        add = QPushButton("Add"); rm = QPushButton("Delete"); save = QPushButton("Save (for latest DR)")

        add.clicked.connect(self._add_row)
        rm.clicked.connect(lambda: self.tbl.removeRow(self.tbl.currentRow()))
        save.clicked.connect(self._save)

        btns.addWidget(add); btns.addWidget(rm); btns.addStretch(1); btns.addWidget(save)
        lay.addLayout(btns); lay.addWidget(self.tbl)

    def _add_row(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        tf, tt = QTimeEdit(), QTimeEdit()
        tf.setTime(QTime(0,0)); tt.setTime(QTime(0,0))
        self.tbl.setCellWidget(r, self.COL_FROM, tf); self.tbl.setCellWidget(r, self.COL_TO, tt)
        self.tbl.setItem(r, self.COL_DUR, QTableWidgetItem("0"))

        main_cb, sub_cb = QComboBox(), QComboBox()
        main_cb.addItem("", None); sub_cb.addItem("", None)
        with session_scope(self.SessionLocal) as s:
            for m in s.query(CodeMain).order_by(CodeMain.phase, CodeMain.code).all():
                main_cb.addItem(f"{m.phase}-{m.code}-{m.name}", m.id)
        main_cb.currentIndexChanged.connect(lambda _=None, row=r: self._reload_sub(row))
        self.tbl.setCellWidget(r, self.COL_MAIN, main_cb)
        self.tbl.setCellWidget(r, self.COL_SUB, sub_cb)

        self.tbl.setItem(r, self.COL_DESC, QTableWidgetItem(""))
        self.tbl.setItem(r, self.COL_RESP, QTableWidgetItem(""))

        tf.timeChanged.connect(lambda _=None, row=r: self._recalc(row))
        tt.timeChanged.connect(lambda _=None, row=r: self._recalc(row))

    def _reload_sub(self, row: int):
        main_cb: QComboBox = self.tbl.cellWidget(row, self.COL_MAIN)  # type: ignore
        sub_cb: QComboBox = self.tbl.cellWidget(row, self.COL_SUB)    # type: ignore
        sub_cb.clear(); sub_cb.addItem("", None)
        mid = main_cb.currentData()
        if not mid: return
        with session_scope(self.SessionLocal) as s:
            for sc in s.query(CodeSub).filter(CodeSub.main_id==mid).order_by(CodeSub.sub_code).all():
                sub_cb.addItem(f"{sc.sub_code}-{sc.name}", sc.id)

    def _recalc(self, row: int):
        tf: QTimeEdit = self.tbl.cellWidget(row, self.COL_FROM)  # type: ignore
        tt: QTimeEdit = self.tbl.cellWidget(row, self.COL_TO)    # type: ignore
        mins = minutes_between(tf.time().toPython(), tt.time().toPython())
        self.tbl.item(row, self.COL_DUR).setText(str(mins))

    def _save(self):
        with session_scope(self.SessionLocal) as s:
            dr = s.query(DailyReport).order_by(DailyReport.report_date.desc()).first()
            if not dr:
                QMessageBox.warning(self, "No DR", "ابتدا Daily Report بسازید")
                return
            s.query(NPTEntry).filter(NPTEntry.daily_report_id==dr.id).delete()
            s.flush()
            for r in range(self.tbl.rowCount()):
                tf: QTimeEdit = self.tbl.cellWidget(r, self.COL_FROM)  # type: ignore
                tt: QTimeEdit = self.tbl.cellWidget(r, self.COL_TO)    # type: ignore
                dur = int(self.tbl.item(r, self.COL_DUR).text()) if self.tbl.item(r, self.COL_DUR) else 0
                main_id = self.tbl.cellWidget(r, self.COL_MAIN).currentData()  # type: ignore
                sub_id = self.tbl.cellWidget(r, self.COL_SUB).currentData()    # type: ignore
                desc = self.tbl.item(r, self.COL_DESC).text() if self.tbl.item(r, self.COL_DESC) else ""
                resp = self.tbl.item(r, self.COL_RESP).text() if self.tbl.item(r, self.COL_RESP) else ""
                s.add(NPTEntry(
                    daily_report_id=dr.id,
                    time_from=tf.time().toPython(),
                    time_to=tt.time().toPython(),
                    duration_min=dur,
                    main_code_id=main_id,
                    sub_code_id=sub_id,
                    description=desc or None,
                    responsible_party=resp or None
                ))
        QMessageBox.information(self, "Saved", "NPT Report ذخیره شد")
