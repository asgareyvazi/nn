# File: modules/cement_casing.py
# Purpose: Cement & Additives inventory per section.

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QDate
from .base import ModuleBase  # فرض می‌کنیم پایه ModuleBase در پروژه هست
from models import CementJob, AdditiveInventory, CasingData  # فرض می‌کنیم مدل‌های دیتابیس

class CementAdditivesWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build()
        self._load_data()

    def _build(self):
        layout = QVBoxLayout(self)

        # --- Cement Jobs Table ---
        self.job_table = QTableWidget(0, 8)
        self.job_table.setHorizontalHeaderLabels([
            "Date", "Job Type", "Volume (sx)", "Additives",
            "Mix Density", "Pressure", "Result", "Remarks"
        ])
        layout.addWidget(self.job_table)

        # --- Additives Inventory Table ---
        self.inv_table = QTableWidget(0, 8)
        self.inv_table.setHorizontalHeaderLabels([
            "Product", "Type", "Received", "Used",
            "Stock", "Unit", "Supplier", "Batch No"
        ])
        layout.addWidget(self.inv_table)

        # --- Casing Information Table ---
        self.casing_table = QTableWidget(0, 10)
        self.casing_table.setHorizontalHeaderLabels([
            "Size", "From", "To", "Grade",
            "Weight", "Thread", "Shoe TVD",
            "Burst", "Collapse", "Centralizers"
        ])
        layout.addWidget(self.casing_table)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.btn_add_job = QPushButton("Add Cement Job")
        self.btn_remove_job = QPushButton("Remove Job")
        self.btn_add_additive = QPushButton("Add Additive")
        self.btn_remove_additive = QPushButton("Remove Additive")
        self.btn_add_casing = QPushButton("Add Casing")
        self.btn_remove_casing = QPushButton("Remove Casing")
        self.btn_save = QPushButton("Save All")

        for btn in [
            self.btn_add_job, self.btn_remove_job,
            self.btn_add_additive, self.btn_remove_additive,
            self.btn_add_casing, self.btn_remove_casing,
            self.btn_save
        ]:
            btn_layout.addWidget(btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Connect signals
        self.btn_add_job.clicked.connect(self._add_job)
        self.btn_remove_job.clicked.connect(lambda: self._remove_selected_row(self.job_table))
        self.btn_add_additive.clicked.connect(self._add_additive)
        self.btn_remove_additive.clicked.connect(lambda: self._remove_selected_row(self.inv_table))
        self.btn_add_casing.clicked.connect(self._add_casing)
        self.btn_remove_casing.clicked.connect(lambda: self._remove_selected_row(self.casing_table))
        self.btn_save.clicked.connect(self._save)

    def _add_job(self):
        row = self.job_table.rowCount()
        self.job_table.insertRow(row)
        # Default date today as string
        self.job_table.setItem(row, 0, QTableWidgetItem(QDate.currentDate().toString("yyyy-MM-dd")))
        for col in range(1, 8):
            self.job_table.setItem(row, col, QTableWidgetItem(""))

    def _add_additive(self):
        row = self.inv_table.rowCount()
        self.inv_table.insertRow(row)
        # Defaults: Received=0, Used=0, Stock=0, Unit=kg
        defaults = ["", "", "0", "0", "0", "kg", "", ""]
        for col, val in enumerate(defaults):
            self.inv_table.setItem(row, col, QTableWidgetItem(val))

    def _add_casing(self):
        row = self.casing_table.rowCount()
        self.casing_table.insertRow(row)
        defaults = ["0"]*10
        for col, val in enumerate(defaults):
            self.casing_table.setItem(row, col, QTableWidgetItem(val))

    def _remove_selected_row(self, table):
        selected = table.selectionModel().selectedRows()
        for index in sorted(selected, key=lambda x: x.row(), reverse=True):
            table.removeRow(index.row())

    def _load_data(self):
        # Clear tables
        self.job_table.setRowCount(0)
        self.inv_table.setRowCount(0)
        self.casing_table.setRowCount(0)

        with self.db.get_session() as session:
            # Load Cement Jobs
            jobs = session.query(CementJob).order_by(CementJob.date.desc()).all()
            for job in jobs:
                row = self.job_table.rowCount()
                self.job_table.insertRow(row)
                self.job_table.setItem(row, 0, QTableWidgetItem(job.date.strftime("%Y-%m-%d") if job.date else ""))
                self.job_table.setItem(row, 1, QTableWidgetItem(job.job_type or ""))
                self.job_table.setItem(row, 2, QTableWidgetItem(str(job.volume or 0)))
                self.job_table.setItem(row, 3, QTableWidgetItem(job.additives or ""))
                self.job_table.setItem(row, 4, QTableWidgetItem(str(job.mix_density or 0)))
                self.job_table.setItem(row, 5, QTableWidgetItem(str(job.pressure or 0)))
                self.job_table.setItem(row, 6, QTableWidgetItem(job.result or ""))
                self.job_table.setItem(row, 7, QTableWidgetItem(job.remarks or ""))

            # Load Additives Inventory
            additives = session.query(AdditiveInventory).order_by(AdditiveInventory.product).all()
            for item in additives:
                row = self.inv_table.rowCount()
                self.inv_table.insertRow(row)
                self.inv_table.setItem(row, 0, QTableWidgetItem(item.product or ""))
                self.inv_table.setItem(row, 1, QTableWidgetItem(item.type or ""))
                self.inv_table.setItem(row, 2, QTableWidgetItem(str(item.received or 0)))
                self.inv_table.setItem(row, 3, QTableWidgetItem(str(item.used or 0)))
                self.inv_table.setItem(row, 4, QTableWidgetItem(str(item.stock or 0)))
                self.inv_table.setItem(row, 5, QTableWidgetItem(item.unit or ""))
                self.inv_table.setItem(row, 6, QTableWidgetItem(item.supplier or ""))
                self.inv_table.setItem(row, 7, QTableWidgetItem(item.batch_no or ""))

            # Load Casing Data
            casings = session.query(CasingData).order_by(CasingData.size).all()
            for item in casings:
                row = self.casing_table.rowCount()
                self.casing_table.insertRow(row)
                self.casing_table.setItem(row, 0, QTableWidgetItem(str(item.size or 0)))
                self.casing_table.setItem(row, 1, QTableWidgetItem(str(item.from_depth or 0)))
                self.casing_table.setItem(row, 2, QTableWidgetItem(str(item.to_depth or 0)))
                self.casing_table.setItem(row, 3, QTableWidgetItem(item.grade or ""))
                self.casing_table.setItem(row, 4, QTableWidgetItem(str(item.weight or 0)))
                self.casing_table.setItem(row, 5, QTableWidgetItem(item.thread or ""))
                self.casing_table.setItem(row, 6, QTableWidgetItem(str(item.shoe_tvd or 0)))
                self.casing_table.setItem(row, 7, QTableWidgetItem(str(item.burst_pressure or 0)))
                self.casing_table.setItem(row, 8, QTableWidgetItem(str(item.collapse_pressure or 0)))
                self.casing_table.setItem(row, 9, QTableWidgetItem(str(item.centralizers or 0)))

    def _save(self):
        try:
            with self.db.get_session() as session:
                # Clear old data
                session.query(CementJob).delete()
                session.query(AdditiveInventory).delete()
                session.query(CasingData).delete()

                # Save Cement Jobs
                for row in range(self.job_table.rowCount()):
                    date_str = self.job_table.item(row, 0).text()
                    job = CementJob(
                        date=QDate.fromString(date_str, "yyyy-MM-dd").toPython() if date_str else None,
                        job_type=self.job_table.item(row, 1).text(),
                        volume=float(self.job_table.item(row, 2).text() or 0),
                        additives=self.job_table.item(row, 3).text(),
                        mix_density=float(self.job_table.item(row, 4).text() or 0),
                        pressure=float(self.job_table.item(row, 5).text() or 0),
                        result=self.job_table.item(row, 6).text(),
                        remarks=self.job_table.item(row, 7).text()
                    )
                    session.add(job)

                # Save Additives Inventory
                for row in range(self.inv_table.rowCount()):
                    item = AdditiveInventory(
                        product=self.inv_table.item(row, 0).text(),
                        type=self.inv_table.item(row, 1).text(),
                        received=float(self.inv_table.item(row, 2).text() or 0),
                        used=float(self.inv_table.item(row, 3).text() or 0),
                        stock=float(self.inv_table.item(row, 4).text() or 0),
                        unit=self.inv_table.item(row, 5).text(),
                        supplier=self.inv_table.item(row, 6).text(),
                        batch_no=self.inv_table.item(row, 7).text()
                    )
                    session.add(item)

                # Save Casing Data
                for row in range(self.casing_table.rowCount()):
                    casing = CasingData(
                        size=float(self.casing_table.item(row, 0).text() or 0),
                        from_depth=float(self.casing_table.item(row, 1).text() or 0),
                        to_depth=float(self.casing_table.item(row, 2).text() or 0),
                        grade=self.casing_table.item(row, 3).text(),
                        weight=float(self.casing_table.item(row, 4).text() or 0),
                        thread=self.casing_table.item(row, 5).text(),
                        shoe_tvd=float(self.casing_table.item(row, 6).text() or 0),
                        burst_pressure=float(self.casing_table.item(row, 7).text() or 0),
                        collapse_pressure=float(self.casing_table.item(row, 8).text() or 0),
                        centralizers=int(self.casing_table.item(row, 9).text() or 0)
                    )
                    session.add(casing)

                session.commit()
            QMessageBox.information(self, "Saved", "All data saved successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving data: {e}")

class CementAdditivesModule(ModuleBase):
    DISPLAY_NAME = "Cement & Additives"

    def __init__(self, db, parent=None):
        super().__init__(db, parent)
        self.widget = CementAdditivesWidget(self.db)

    def get_widget(self):
        return self.widget
