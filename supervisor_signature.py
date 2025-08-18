
# =========================================
# file: nikan_drill_master/modules/supervisor_signature.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox, QPushButton, QMessageBox
from modules.base import ModuleBase
from database import session_scope
from sqlalchemy.orm import Session
from models import SupervisorSignature, DailyReport

class SupervisorSignatureModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.supervisor = QLineEdit()
        self.op_manager = QLineEdit()
        self.approved = QCheckBox("Approved")
        save = QPushButton("Save (for latest DR)")
        save.clicked.connect(self._save)
        form.addRow("Supervisor Name", self.supervisor)
        form.addRow("Operation Manager", self.op_manager)
        form.addRow("", self.approved)
        lay.addLayout(form); lay.addWidget(save)

    def _save(self):
        from datetime import datetime
        with session_scope(self.SessionLocal) as s:
            dr = s.query(DailyReport).order_by(DailyReport.report_date.desc()).first()
            if not dr:
                QMessageBox.warning(self, "No DR", "ابتدا Daily Report بسازید")
                return
            sig = s.query(SupervisorSignature).filter(SupervisorSignature.daily_report_id==dr.id).one_or_none()
            if not sig:
                sig = SupervisorSignature(daily_report_id=dr.id)
                s.add(sig)
            sig.supervisor_name = self.supervisor.text().strip() or None
            sig.operation_manager = self.op_manager.text().strip() or None
            sig.approved = self.approved.isChecked()
            sig.approved_at = datetime.utcnow() if sig.approved else None
        QMessageBox.information(self, "Saved", "Signature ثبت شد")
