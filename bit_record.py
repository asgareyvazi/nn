# -*- coding: utf-8 -*-
"""
modules/bit_record.py

Bit master + per-bit run report (before/after photo paths).

Uses:
- PySide6 for UI
- BaseModule (base.BaseModule) pattern for consistent module lifecycle
- Database.get_session() context manager for safe DB access
- SQLAlchemy 1.4+ style session.get where appropriate
"""
from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox
)

from base import BaseModule
from models import Section, BitRecord, BitRunReport

logger = logging.getLogger(__name__)


class BitRecordWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_bit: Optional[BitRecord] = None
        self._build()
        self._load_sections()

    def _build(self) -> None:
        v = QVBoxLayout(self)

        # Section selector
        self.cb_section = QComboBox()
        v.addWidget(self.cb_section)

        # Form layout
        frm = QFormLayout()
        v.addLayout(frm)

        # Input fields
        self.le_bit_no = QLineEdit()
        self.sp_size = QDoubleSpinBox()
        self.sp_size.setRange(0, 60)
        self.le_manu = QLineEdit()
        self.le_type = QLineEdit()
        self.le_sn = QLineEdit()
        self.le_iadc = QLineEdit()
        self.le_dull = QLineEdit()
        self.le_reason = QLineEdit()
        self.sp_in = QDoubleSpinBox()
        self.sp_out = QDoubleSpinBox()
        self.sp_hours = QDoubleSpinBox()
        self.sp_cum_drilled = QDoubleSpinBox()
        self.sp_cum_hours = QDoubleSpinBox()
        self.sp_rop = QDoubleSpinBox()
        self.le_formation = QLineEdit()
        self.le_lith = QLineEdit()

        # Set ranges and decimals
        for w in [self.sp_size, self.sp_in, self.sp_out, self.sp_hours, self.sp_cum_drilled,
                  self.sp_cum_hours, self.sp_rop]:
            w.setRange(0, 1e6)
            w.setDecimals(2)

        # Add rows to form layout
        frm.addRow("Bit No", self.le_bit_no)
        frm.addRow("Size (in)", self.sp_size)
        frm.addRow("Manufacturer", self.le_manu)
        frm.addRow("Type", self.le_type)
        frm.addRow("Serial No", self.le_sn)
        frm.addRow("IADC Code", self.le_iadc)
        frm.addRow("Dull Grading", self.le_dull)
        frm.addRow("Reason Pulled", self.le_reason)
        frm.addRow("Depth In/Out", self._pair(self.sp_in, self.sp_out))
        frm.addRow("Hours / Cum Drilled / Cum Hrs / ROP", self._quad(self.sp_hours, self.sp_cum_drilled,
                                                                     self.sp_cum_hours, self.sp_rop))
        frm.addRow("Formation / Lithology", self._pair(self.le_formation, self.le_lith))

        # Runs table
        self.tbl = QTableWidget(0, 10)
        self.tbl.setHorizontalHeaderLabels(
            ["WOB", "RPM", "Flowrate", "SPP", "PV", "YP", "Cum Drill", "ROP", "TFA", "Revolution"]
        )
        v.addWidget(self.tbl)

        # Buttons
        hb = QHBoxLayout()
        self.btn_add = QPushButton("Add Run")
        self.btn_del = QPushButton("Delete Selected")
        hb.addWidget(self.btn_add)
        hb.addWidget(self.btn_del)
        v.addLayout(hb)

        # Save button
        save = QPushButton("Save Bit")
        save.clicked.connect(self._save)
        v.addWidget(save)

        # Connect signals
        self.btn_add.clicked.connect(self._add_run)
        self.btn_del.clicked.connect(self._del_run)
        self.cb_section.currentIndexChanged.connect(self._load_bit)

    def _pair(self, a, b):
        from PySide6.QtWidgets import QWidget, QHBoxLayout
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(a)
        l.addWidget(b)
        return w

    def _quad(self, a, b, c, d):
        from PySide6.QtWidgets import QWidget, QHBoxLayout
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        [l.addWidget(x) for x in (a, b, c, d)]
        return w

    def _load_sections(self) -> None:
        """Populate section combobox."""
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
            for r in rows:
                self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _load_bit(self) -> None:
        """Load bit record for selected section."""
        sid = self.cb_section.currentData()
        if sid is None:
            return
        with self.db.get_session() as s:
            bit = s.query(BitRecord).filter_by(section_id=sid).first()
            if bit:
                self.current_bit = bit
                self.le_bit_no.setText(bit.bit_no or "")
                self.sp_size.setValue(bit.size_in or 0)
                self.le_manu.setText(bit.manufacturer or "")
                self.le_type.setText(bit.type or "")
                self.le_sn.setText(bit.serial_no or "")
                self.le_iadc.setText(bit.iadc_code or "")
                self.le_dull.setText(bit.dull_grading or "")
                self.le_reason.setText(bit.reason_pulled or "")
                self.sp_in.setValue(bit.depth_in or 0)
                self.sp_out.setValue(bit.depth_out or 0)
                self.sp_hours.setValue(bit.hours or 0)
                self.sp_cum_drilled.setValue(bit.cum_drilled or 0)
                self.sp_cum_hours.setValue(bit.cum_hours or 0)
                self.sp_rop.setValue(bit.rop or 0)
                self.le_formation.setText(bit.formation or "")
                self.le_lith.setText(bit.lithology or "")
                self._load_runs(bit.id)

    def _load_runs(self, bit_id: int) -> None:
        """Load run reports for selected bit."""
        self.tbl.setRowCount(0)
        with self.db.get_session() as s:
            runs = s.query(BitRunReport).filter_by(bit_id=bit_id).all()
            for r in runs:
                row = self.tbl.rowCount()
                self.tbl.insertRow(row)
                self.tbl.setItem(row, 0, QTableWidgetItem(str(r.wob or 0)))
                self.tbl.setItem(row, 1, QTableWidgetItem(str(r.rpm or 0)))
                self.tbl.setItem(row, 2, QTableWidgetItem(str(r.flowrate or 0)))
                self.tbl.setItem(row, 3, QTableWidgetItem(str(r.spp or 0)))
                self.tbl.setItem(row, 4, QTableWidgetItem(str(r.pv or 0)))
                self.tbl.setItem(row, 5, QTableWidgetItem(str(r.yp or 0)))
                self.tbl.setItem(row, 6, QTableWidgetItem(str(r.cumulative_drilling or 0)))
                self.tbl.setItem(row, 7, QTableWidgetItem(str(r.rop or 0)))
                self.tbl.setItem(row, 8, QTableWidgetItem(str(r.tfa or 0)))
                self.tbl.setItem(row, 9, QTableWidgetItem(str(r.revolution or 0)))

    def _add_run(self) -> None:
        """Add a new run to the table."""
        row = self.tbl.rowCount()
        self.tbl.insertRow(row)
        for col in range(10):
            self.tbl.setItem(row, col, QTableWidgetItem("0"))

    def _del_run(self) -> None:
        """Delete selected run from the table."""
        selected_rows = self.tbl.selectionModel().selectedRows()
        for row in sorted([r.row() for r in selected_rows], reverse=True):
            self.tbl.removeRow(row)

    def _save(self) -> None:
        """Save bit record and its run reports."""
        sid = self.cb_section.currentData()
        if sid is None:
            QMessageBox.warning(self, "No Section", "Please select a section first.")
            return

        with self.db.get_session() as s:
            # Save BitRecord
            if self.current_bit is None:
                bit = BitRecord(section_id=sid)
                s.add(bit)
                s.flush()
            else:
                bit = self.current_bit

            bit.bit_no = self.le_bit_no.text().strip()
            bit.size_in = self.sp_size.value()
            bit.manufacturer = self.le_manu.text().strip()
            bit.type = self.le_type.text().strip()
            bit.serial_no = self.le_sn.text().strip()
            bit.iadc_code = self.le_iadc.text().strip()
            bit.dull_grading = self.le_dull.text().strip()
            bit.reason_pulled = self.le_reason.text().strip()
            bit.depth_in = self.sp_in.value()
            bit.depth_out = self.sp_out.value
::contentReference[oaicite:0]{index=0}
 
