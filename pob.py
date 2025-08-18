
# =========================================
# file: nikan_drill_master/modules/pob.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QTableWidgetItem, QMessageBox, QComboBox, QDateEdit
from sqlalchemy.orm import Session
from modules.base import ModuleBase
from database import session_scope
from models import POBEntry, Section

class POBModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._section_id: int | None = None
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels(["Company/Service","Service Type","No.","Date IN","Category"])
        btns = QHBoxLayout()
        add = QPushButton("Add"); rm = QPushButton("Delete"); save = QPushButton("Save")
        add.clicked.connect(lambda: self.tbl.insertRow(self.tbl.rowCount()))
        rm.clicked.connect(lambda: self.tbl.removeRow(self.tbl.currentRow()))
        save.clicked.connect(self._save)
        btns.addWidget(add); btns.addWidget(rm); btns.addStretch(1); btns.addWidget(save)
        lay.addLayout(btns); lay.addWidget(self.tbl)

    def on_selection_changed(self, context: dict) -> None:
        sel = context.get("selection")
        if sel and sel[0] == "section":
            self._section_id = int(sel[1])

    def _save(self):
        if not self._section_id:
            QMessageBox.warning(self, "Selection", "Section را از درخت انتخاب کنید")
            return
        with session_scope(self.SessionLocal) as s:
            s.query(POBEntry).filter(POBEntry.section_id==self._section_id).delete()
            s.flush()
            for r in range(self.tbl.rowCount()):
                name = self.tbl.item(r,0).text() if self.tbl.item(r,0) else ""
                service = self.tbl.item(r,1).text() if self.tbl.item(r,1) else ""
                try: count = int(self.tbl.item(r,2).text()) if self.tbl.item(r,2) else 0
                except Exception: count = 0
                try:
                    date_in = self.tbl.cellWidget(r,3).date().toPython() if isinstance(self.tbl.cellWidget(r,3), QDateEdit) else None
                except Exception:
                    date_in = None
                category = self.tbl.item(r,4).text() if self.tbl.item(r,4) else ""
                if not isinstance(self.tbl.cellWidget(r,3), QDateEdit):
                    de = QDateEdit(); de.setCalendarPopup(True); self.tbl.setCellWidget(r,3,de)
                s.add(POBEntry(section_id=self._section_id, company_name=name, service=service or None, count=count, date_in=date_in, category=category or None))
        QMessageBox.information(self, "Saved", "POB ذخیره شد")
