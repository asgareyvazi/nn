from PySide2.QtCore import Qt, QDate
from PySide2.QtWidgets import (
    QTableView, QPushButton, QHBoxLayout, QWidget,
    QStyledItemDelegate, QDateEdit
)
from PySide2.QtGui import QStandardItemModel, QStandardItem
from modules.base import ModuleBase


class DateDelegate(QStyledItemDelegate):
    """Delegate for displaying and editing dates in table cells"""
    def createEditor(self, parent, option, index):
        editor = QDateEdit(parent)
        editor.setDisplayFormat("yyyy-MM-dd")
        editor.setCalendarPopup(True)
        return editor


class CementAdditivesModule(ModuleBase):
    """
    Cement & Additives Module:
    Comprehensive management of cement jobs, additives inventory, and casing data
    with full database integration.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__("Cement & Additives", parent)
        self._setup_ui()
        self._configure_tables()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize all UI components"""
        # --- Cement Jobs Table ---
        job_headers = [
            "Date", "Job Type", "Volume (sx)", "Additives",
            "Mix Density (ppg)", "Pressure (psi)", "Result", "Remarks"
        ]
        self.job_group, self.job_table, self.job_model = self.create_table_group(
            "Cement Jobs", job_headers
        )

        # --- Additives Inventory Table ---
        inv_headers = [
            "Product", "Type", "Received", "Used",
            "Stock", "Unit", "Supplier", "Batch No"
        ]
        self.inv_group, self.inv_table, self.inv_model = self.create_table_group(
            "Additives Inventory", inv_headers
        )

        # --- Casing Information Table ---
        casing_headers = [
            "Size (in)", "From (m)", "To (m)", "Grade",
            "Weight (#)", "Thread", "Shoe (TVD m)",
            "Burst (psi)", "Collapse (psi)", "Centralizers"
        ]
        self.casing_group, self.casing_table, self.casing_model = self.create_table_group(
            "Casing Information", casing_headers
        )

        # --- Control Buttons ---
        self.btn_layout = QHBoxLayout()
        self.btn_add_job = QPushButton("Add Cement Job")
        self.btn_remove_job = QPushButton("Remove Job")
        self.btn_add_additive = QPushButton("Add Additive")
        self.btn_remove_additive = QPushButton("Remove Additive")
        self.btn_add_casing = QPushButton("Add Casing")
        self.btn_remove_casing = QPushButton("Remove Casing")
        self.btn_save = QPushButton("Save All")

        for btn in (
            self.btn_add_job, self.btn_remove_job,
            self.btn_add_additive, self.btn_remove_additive,
            self.btn_add_casing, self.btn_remove_casing,
            self.btn_save
        ):
            self.btn_layout.addWidget(btn)
        self.btn_layout.addStretch()

        # --- Assemble Layout ---
        self.scroll_layout.addWidget(self.job_group)
        self.scroll_layout.addWidget(self.inv_group)
        self.scroll_layout.addWidget(self.casing_group)
        self.scroll_layout.addLayout(self.btn_layout)
        self.scroll_layout.addStretch()

    def _configure_tables(self) -> None:
        """Configure table properties and delegates"""
        # Common table settings
        for table in [self.job_table, self.inv_table, self.casing_table]:
            table.setSelectionBehavior(QTableView.SelectRows)
            table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
            table.horizontalHeader().setStretchLastSection(True)

        # Set date delegate for cement jobs
        date_delegate = DateDelegate()
        self.job_table.setItemDelegateForColumn(0, date_delegate)

        # Configure models
        self.job_model.setHorizontalHeaderLabels([
            "Date", "Job Type", "Volume (sx)", "Additives",
            "Mix Density", "Pressure", "Result", "Remarks"
        ])

        self.inv_model.setHorizontalHeaderLabels([
            "Product", "Type", "Received", "Used",
            "Stock", "Unit", "Supplier", "Batch No"
        ])

        self.casing_model.setHorizontalHeaderLabels([
            "Size", "From", "To", "Grade",
            "Weight", "Thread", "Shoe TVD",
            "Burst", "Collapse", "Centralizers"
        ])

    def _connect_signals(self) -> None:
        """Connect button signals to their handlers"""
        self.btn_add_job.clicked.connect(self._add_cement_job)
        self.btn_remove_job.clicked.connect(lambda: self._remove_selected_row(self.job_model, self.job_table))
        self.btn_add_additive.clicked.connect(self._add_additive)
        self.btn_remove_additive.clicked.connect(lambda: self._remove_selected_row(self.inv_model, self.inv_table))
        self.btn_add_casing.clicked.connect(self._add_casing)
        self.btn_remove_casing.clicked.connect(lambda: self._remove_selected_row(self.casing_model, self.casing_table))
        self.btn_save.clicked.connect(self.save_data)

    def _add_cement_job(self) -> None:
        """Add new cement job record"""
        row = self.job_model.rowCount()
        items = [
            QStandardItem(),  # Date
            QStandardItem(),  # Job Type
            QStandardItem("0"),  # Volume
            QStandardItem(),  # Additives
            QStandardItem("0"),  # Mix Density
            QStandardItem("0"),  # Pressure
            QStandardItem(),  # Result
            QStandardItem()   # Remarks
        ]
        
        # Set current date as default
        items[0].setData(QDate.currentDate(), Qt.DisplayRole)
        
        for item in items:
            item.setEditable(True)
            
        self.job_model.insertRow(row, items)
        self.job_table.selectRow(row)

    def _add_additive(self) -> None:
        """Add new additive to inventory"""
        row = self.inv_model.rowCount()
        items = [
            QStandardItem(),  # Product
            QStandardItem(),  # Type
            QStandardItem("0"),  # Received
            QStandardItem("0"),  # Used
            QStandardItem("0"),  # Stock
            QStandardItem("kg"),  # Unit
            QStandardItem(),  # Supplier
            QStandardItem()   # Batch No
        ]
        
        for item in items:
            item.setEditable(True)
            
        self.inv_model.insertRow(row, items)
        self.inv_table.selectRow(row)

    def _add_casing(self) -> None:
        """Add new casing record"""
        row = self.casing_model.rowCount()
        items = [
            QStandardItem("0"),  # Size
            QStandardItem("0"),  # From
            QStandardItem("0"),  # To
            QStandardItem(),  # Grade
            QStandardItem("0"),  # Weight
            QStandardItem(),  # Thread
            QStandardItem("0"),  # Shoe TVD
            QStandardItem("0"),  # Burst
            QStandardItem("0"),  # Collapse
            QStandardItem("0")   # Centralizers
        ]
        
        for item in items:
            item.setEditable(True)
            
        self.casing_model.insertRow(row, items)
        self.casing_table.selectRow(row)

    def _remove_selected_row(self, model: QStandardItemModel, table: QTableView) -> None:
        """Remove selected row from specified table"""
        sel = table.selectionModel()
        if sel.hasSelection():
            row = sel.selectedRows()[0].row()
            model.removeRow(row)

    def load_data(self) -> None:
        """
        Load data from database into all tables
        """
        try:
            # Load cement jobs
            jobs = self.db.execute_query(
                "SELECT * FROM cement_jobs ORDER BY date DESC"
            ).fetchall()
            
            self.job_model.removeRows(0, self.job_model.rowCount())
            for job in jobs:
                row = [
                    QStandardItem(),
                    QStandardItem(job['job_type']),
                    QStandardItem(str(job['volume'])),
                    QStandardItem(job['additives']),
                    QStandardItem(str(job['mix_density'])),
                    QStandardItem(str(job['pressure'])),
                    QStandardItem(job['result']),
                    QStandardItem(job['remarks'])
                ]
                
                # Set date
                date = QDate.fromString(job['date'], "yyyy-MM-dd")
                row[0].setData(date, Qt.DisplayRole)
                
                for item in row:
                    item.setEditable(True)
                    
                self.job_model.appendRow(row)
            
            # Load additives
            additives = self.db.execute_query(
                "SELECT * FROM additives_inventory ORDER BY product"
            ).fetchall()
            
            self.inv_model.removeRows(0, self.inv_model.rowCount())
            for additive in additives:
                row = [
                    QStandardItem(additive['product']),
                    QStandardItem(additive['type']),
                    QStandardItem(str(additive['received'])),
                    QStandardItem(str(additive['used'])),
                    QStandardItem(str(additive['stock'])),
                    QStandardItem(additive['unit']),
                    QStandardItem(additive['supplier']),
                    QStandardItem(additive['batch_no'])
                ]
                
                for item in row:
                    item.setEditable(True)
                    
                self.inv_model.appendRow(row)
            
            # Load casing data
            casings = self.db.execute_query(
                "SELECT * FROM casing_data ORDER BY size"
            ).fetchall()
            
            self.casing_model.removeRows(0, self.casing_model.rowCount())
            for casing in casings:
                row = [
                    QStandardItem(str(casing['size'])),
                    QStandardItem(str(casing['from_depth'])),
                    QStandardItem(str(casing['to_depth'])),
                    QStandardItem(casing['grade']),
                    QStandardItem(str(casing['weight'])),
                    QStandardItem(casing['thread']),
                    QStandardItem(str(casing['shoe_tvd'])),
                    QStandardItem(str(casing['burst_pressure'])),
                    QStandardItem(str(casing['collapse_pressure'])),
                    QStandardItem(str(casing['centralizers']))
                ]
                
                for item in row:
                    item.setEditable(True)
                    
                self.casing_model.appendRow(row)
                
        except Exception as e:
            print(f"Error loading data: {str(e)}")

    def save_data(self) -> None:
        """
        Save all changes to database
        """
        try:
            # Begin transaction
            self.db.execute_query("BEGIN TRANSACTION")
            
            # Clear existing records
            self.db.execute_query("DELETE FROM cement_jobs")
            self.db.execute_query("DELETE FROM additives_inventory")
            self.db.execute_query("DELETE FROM casing_data")
            
            # Save cement jobs
            for row in range(self.job_model.rowCount()):
                record = {
                    'date': self.job_model.item(row, 0).data(Qt.DisplayRole).toString("yyyy-MM-dd"),
                    'job_type': self.job_model.item(row, 1).text(),
                    'volume': float(self.job_model.item(row, 2).text()),
                    'additives': self.job_model.item(row, 3).text(),
                    'mix_density': float(self.job_model.item(row, 4).text()),
                    'pressure': float(self.job_model.item(row, 5).text()),
                    'result': self.job_model.item(row, 6).text(),
                    'remarks': self.job_model.item(row, 7).text()
                }
                
                self.db.execute_query(
                    """INSERT INTO cement_jobs 
                    (date, job_type, volume, additives, mix_density, pressure, result, remarks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    tuple(record.values())
                )
            
            # Save additives
            for row in range(self.inv_model.rowCount()):
                record = {
                    'product': self.inv_model.item(row, 0).text(),
                    'type': self.inv_model.item(row, 1).text(),
                    'received': float(self.inv_model.item(row, 2).text()),
                    'used': float(self.inv_model.item(row, 3).text()),
                    'stock': float(self.inv_model.item(row, 4).text()),
                    'unit': self.inv_model.item(row, 5).text(),
                    'supplier': self.inv_model.item(row, 6).text(),
                    'batch_no': self.inv_model.item(row, 7).text()
                }
                
                self.db.execute_query(
                    """INSERT INTO additives_inventory 
                    (product, type, received, used, stock, unit, supplier, batch_no)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    tuple(record.values())
                )
            
            # Save casing data
            for row in range(self.casing_model.rowCount()):
                record = {
                    'size': float(self.casing_model.item(row, 0).text()),
                    'from_depth': float(self.casing_model.item(row, 1).text()),
                    'to_depth': float(self.casing_model.item(row, 2).text()),
                    'grade': self.casing_model.item(row, 3).text(),
                    'weight': float(self.casing_model.item(row, 4).text()),
                    'thread': self.casing_model.item(row, 5).text(),
                    'shoe_tvd': float(self.casing_model.item(row, 6).text()),
                    'burst_pressure': float(self.casing_model.item(row, 7).text()),
                    'collapse_pressure': float(self.casing_model.item(row, 8).text()),
                    'centralizers': int(self.casing_model.item(row, 9).text())
                }
                
                self.db.execute_query(
                    """INSERT INTO casing_data 
                    (size, from_depth, to_depth, grade, weight, thread, shoe_tvd, 
                     burst_pressure, collapse_pressure, centralizers)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    tuple(record.values())
                )
            
            # Commit transaction
            self.db.execute_query("COMMIT")
            
        except Exception as e:
            self.db.execute_query("ROLLBACK")
            print(f"Error saving data: {str(e)}")
            raise

    def clear_tables(self) -> None:
        """Clear all tables"""
        self.job_model.removeRows(0, self.job_model.rowCount())
        self.inv_model.removeRows(0, self.inv_model.rowCount())
        self.casing_model.removeRows(0, self.casing_model.rowCount())