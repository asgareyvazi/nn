# File: modules/trajectory.py
# Purpose: Trip sheet / trajectory helper: simple calculator from surveys (cumulative MD/Inc/Azi)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, Survey

class TrajectoryWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.txt = QTextEdit(); self.l.addWidget(self.txt)
        self.btn_calc = QPushButton("Build Trajectory Summary"); self.l.addWidget(self.btn_calc)
        self.btn_calc.clicked.connect(self._build_summary)
        self._load_sections()

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _build_summary(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            surveys = s.query(Survey).filter_by(section_id=sid).order_by(Survey.md).all()
        if not surveys:
            QMessageBox.information(self, "No data", "No survey data for this section")
            return
        lines = ["MD,Inc,TVD,Azi,North,East,DLS"]
        for sv in surveys:
            lines.append(",".join([str(getattr(sv, key) or "") for key in ("md","inc","tvd","azi","north","east","dls")]))
        self.txt.setPlainText("\n".join(lines))

class TrajectoryModule(BaseModule):
    DISPLAY_NAME = "Trajectory"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = TrajectoryWidget(self.db)
    def get_widget(self): return self.widget
