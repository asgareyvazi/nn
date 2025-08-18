
# =========================================
# file: nikan_drill_master/modules/survey_data.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QTableWidgetItem, QMessageBox
from sqlalchemy.orm import Session
from modules.base import ModuleBase
from database import session_scope
from models import Survey, Section

class SurveyDataModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._section_id: int | None = None
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        self.tbl = QTableWidget(0, 9)
        self.tbl.setHorizontalHeaderLabels(["MD","Inc","TVD","Azi","North","East","VS/HD","DLS","Tool"])
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
            s.query(Survey).filter(Survey.section_id==self._section_id).delete()
            s.flush()
            for r in range(self.tbl.rowCount()):
                def gf(c):
                    try: return float(self.tbl.item(r, c).text())
                    except Exception: return None
                def gs(c):
                    return self.tbl.item(r, c).text() if self.tbl.item(r,c) else ""
                s.add(Survey(
                    section_id=self._section_id,
                    md=gf(0), inc=gf(1), tvd=gf(2), azi=gf(3),
                    north=gf(4), east=gf(5), vs_hd=gf(6), dls=gf(7),
                    tool=gs(8) or None
                ))
        QMessageBox.information(self, "Saved", "Survey ذخیره شد")
