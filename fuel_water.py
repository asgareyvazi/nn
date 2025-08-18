from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QTableWidgetItem, QMessageBox
from modules.base import ModuleBase
from database import session_scope
from models import FuelWaterDailyItem, FuelWaterBulk, DailyReport

class FuelWaterModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        # Table 1: Daily Consumption
        self.tbl_daily = QTableWidget(0, 4)
        self.tbl_daily.setHorizontalHeaderLabels(["Description","Consumed","Stock","Unit"])
        # Table 2: Bulk data
        self.tbl_bulk = QTableWidget(0, 5)
        self.tbl_bulk.setHorizontalHeaderLabels(["Name","Stock","Used","Received","Unit"])

        btns1 = QHBoxLayout(); add1 = QPushButton("Add Daily"); rm1 = QPushButton("Delete"); btns1.addWidget(add1); btns1.addWidget(rm1); btns1.addStretch(1)
        add1.clicked.connect(lambda: self.tbl_daily.insertRow(self.tbl_daily.rowCount()))
        rm1.clicked.connect(lambda: self.tbl_daily.removeRow(self.tbl_daily.currentRow()))

        btns2 = QHBoxLayout(); add2 = QPushButton("Add Bulk"); rm2 = QPushButton("Delete"); save = QPushButton("Save (latest DR)")
        add2.clicked.connect(lambda: self.tbl_bulk.insertRow(self.tbl_bulk.rowCount()))
        rm2.clicked.connect(lambda: self.tbl_bulk.removeRow(self.tbl_bulk.currentRow()))
        save.clicked.connect(self._save)
        btns2.addWidget(add2); btns2.addWidget(rm2); btns2.addStretch(1); btns2.addWidget(save)

        lay.addWidget(self.tbl_daily); lay.addLayout(btns1)
        lay.addWidget(self.tbl_bulk); lay.addLayout(btns2)

    def _save(self):
        with session_scope(self.SessionLocal) as s:
            dr = s.query(DailyReport).order_by(DailyReport.report_date.desc()).first()
            if not dr:
                QMessageBox.warning(self, "No DR", "ابتدا Daily Report بسازید")
                return
            s.query(FuelWaterDailyItem).filter(FuelWaterDailyItem.daily_report_id==dr.id).delete()
            s.query(FuelWaterBulk).filter(FuelWaterBulk.daily_report_id==dr.id).delete()
            s.flush()

            # daily
            for r in range(self.tbl_daily.rowCount()):
                desc = self.tbl_daily.item(r,0).text() if self.tbl_daily.item(r,0) else ""
                def gf(c):
                    try: return float(self.tbl_daily.item(r, c).text())
                    except Exception: return None
                unit = self.tbl_daily.item(r,3).text() if self.tbl_daily.item(r,3) else ""
                if desc:
                    s.add(FuelWaterDailyItem(
                        daily_report_id=dr.id, description=desc,
                        consumed=gf(1), stock=gf(2), unit=unit or None
                    ))
            # bulk
            for r in range(self.tbl_bulk.rowCount()):
                name = self.tbl_bulk.item(r,0).text() if self.tbl_bulk.item(r,0) else ""
                def gf(c):
                    try: return float(self.tbl_bulk.item(r, c).text())
                    except Exception: return None
                unit = self.tbl_bulk.item(r,4).text() if self.tbl_bulk.item(r,4) else ""
                if name:
                    s.add(FuelWaterBulk(
                        daily_report_id=dr.id, name=name,
                        stock=gf(1), used=gf(2), received=gf(3), unit=unit or None
                    ))
        QMessageBox.information(self, "Saved", "Fuel & Water ذخیره شد")
