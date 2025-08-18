
# =========================================
# file: nikan_drill_master/modules/drilling_parameters.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QPushButton, QVBoxLayout, QMessageBox
from sqlalchemy.orm import Session
from database import session_scope
from modules.base import ModuleBase
from models import DrillingParameters, DailyReport
from datetime import date

class DrillingParametersModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        self.form = QFormLayout()
        self.fields = {}
        def add(name: str, decimals=2, minimum=-1e9, maximum=1e9):
            sb = QDoubleSpinBox(); sb.setDecimals(decimals); sb.setRange(minimum, maximum); sb.setSingleStep(0.1)
            self.fields[name] = sb; self.form.addRow(name, sb)
        for n in [
            "wob_min","wob_max","surf_rpm_min","surf_rpm_max","motor_rpm_min","motor_rpm_max",
            "torque_min","torque_max","pump_press_min","pump_press_max","pump_out_min","pump_out_max",
            "hsi","annular_velocity","tfa","bit_revolution",
            "scr_spm1","scr_spp1","scr_spm2","scr_spp2","scr_spm3","scr_spp3"
        ]:
            add(n, 2, -1e6, 1e6)
        save = QPushButton("Save for current DR (by date in Daily Report)")
        save.clicked.connect(self._save)
        lay.addLayout(self.form); lay.addWidget(save)

    def _save(self):
        # چرا: DR با همان تاریخی که در ماژول DailyReport ذخیره شده باید انتخاب شود
        # این نسخه‌ی سریع: نزدیک‌ترین DR امروز را استفاده می‌کند یا خطا می‌دهد.
        with session_scope(self.SessionLocal) as s:
            dr = s.query(DailyReport).order_by(DailyReport.report_date.desc()).first()
            if not dr:
                QMessageBox.warning(self, "No DR", "ابتدا یک Daily Report بسازید")
                return
            dp = dr.drilling_params
            if not dp:
                dp = DrillingParameters(daily_report_id=dr.id)
                s.add(dp)
            for k, sb in self.fields.items():
                setattr(dp, k, sb.value())

        QMessageBox.information(self, "Saved", "Drilling Parameters ذخیره شد")
