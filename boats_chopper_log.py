# -*- coding: utf-8 -*-
"""
modules/boats_chopper_log.py

Boats & Chopper logs.

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
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)

from base import BaseModule
from models import Section, BoatLog, ChopperLog

logger = logging.getLogger(__name__)


class BoatsChopperWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build()
        self._load_sections()

    def _build(self) -> None:
        v = QVBoxLayout(self)

        # Section selector
        self.cb_section = QComboBox()
        v.addWidget(self.cb_section)

        # Boats table
        self.tbl_boats = QTableWidget(0, 4)
        self.tbl_boats.setHorizontalHeaderLabels(["Name", "Arrival", "Departure", "Status"])
        v.addWidget(self.tbl_boats)

        # Choppers table
        self.tbl_choppers = QTableWidget(0, 4)
        self.tbl_choppers.setHorizontalHeaderLabels(["Name", "Arrival", "Departure", "PAX IN"])
        v.addWidget(self.tbl_choppers)

        # Buttons
        h = QHBoxLayout()
        self.btn_add = QPushButton("Add Row")
        self.btn_del = QPushButton("Delete Selected")
        self.btn_save = QPushButton("Save")
        h.addWidget(self.btn_add)
        h.addWidget(self.btn_del)
        h.addWidget(self.btn_save)
        v.addLayout(h)

        # Connect signals
        self.btn_add.clicked.connect(self._add)
        self.btn_del.clicked.connect(self._del)
        self.btn_save.clicked.connect(self._save)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _load_sections(self) -> None:
        """Populate section combobox."""
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
            for r in rows:
                self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _add(self) -> None:
        """Add a new row to both tables."""
        self.tbl_boats.insertRow(self.tbl_boats.rowCount())
        self.tbl_choppers.insertRow(self.tbl_choppers.rowCount())

    def _del(self) -> None:
        """Delete selected rows from both tables."""
        selected_rows_boats = [i.row() for i in self.tbl_boats.selectionModel().selectedRows()]
        selected_rows_choppers = [i.row() for i in self.tbl_choppers.selectionModel().selectedRows()]
        for row in sorted(selected_rows_boats + selected_rows_choppers, reverse=True):
            if row < self.tbl_boats.rowCount():
                self.tbl_boats.removeRow(row)
            else:
                self.tbl_choppers.removeRow(row - self.tbl_boats.rowCount())

    def _load(self) -> None:
        """Load logs for selected section."""
        sid = self.cb_section.currentData()
        if sid is None:
            return
        with self.db.get_session() as s:
            boats = s.query(BoatLog).filter_by(section_id=sid).all()
            choppers = s.query(ChopperLog).filter_by(section_id=sid).all()
            self.tbl_boats.setRowCount(0)
            self.tbl_choppers.setRowCount(0)
            for b in boats:
                row = self.tbl_boats.rowCount()
                self.tbl_boats.insertRow(row)
                self.tbl_boats.setItem(row, 0, QTableWidgetItem(b.name or ""))
                self.tbl_boats.setItem(row, 1, QTableWidgetItem(str(b.arrival or "")))
                self.tbl_boats.setItem(row, 2, QTableWidgetItem(str(b.departure or "")))
                self.tbl_boats.setItem(row, 3, QTableWidgetItem(b.status or ""))
            for c in choppers:
                row = self.tbl_choppers.rowCount()
                self.tbl_choppers.insertRow(row)
                self.tbl_choppers.setItem(row, 0, QTableWidgetItem(c.name or ""))
                self.tbl_choppers.setItem(row, 1, QTableWidgetItem(str(c.arrival or "")))
                self.tbl_choppers.setItem(row, 2, QTableWidgetItem(str(c.departure or "")))
                self.tbl_choppers.setItem(row, 3, QTableWidgetItem(str(c.pax_in or "")))

    def _save(self) -> None:
        """Save logs to the database."""
        sid = self.cb_section.currentData()
        if sid is None:
            return
        with self.db.get_session() as s:
            # Delete existing logs
            for rec in s.query(BoatLog).filter_by(section_id=sid).all():
                s.delete(rec)
            for rec in s.query(ChopperLog).filter_by(section_id=sid).all():
                s.delete(rec)

            # Save BoatLogs
            for r in range(self.tbl_boats.rowCount()):
                name = self.tbl_boats.item(r, 0).text().strip()
                if not name:
                    continue
                arrival = self.tbl_boats.item(r, 1).text().strip()
                departure = self.tbl_boats.item(r, 2).text().strip()
                status = self.tbl_boats.item(r, 3).text().strip() if self.tbl_boats.item(r, 3) else ""
                s.add(BoatLog(section_id=sid, name=name, arrival=arrival, departure=departure, status=status))

            # Save ChopperLogs
            for r in range(self.tbl_choppers.rowCount()):
                name = self.tbl_choppers.item(r, 0).text().strip()
                if not name:
                    continue
                arrival = self.tbl_choppers.item(r, 1).text().strip()
                departure = self.tbl_choppers.item(r, 2).text().strip()
                pax_in = self.tbl_choppers.item(r, 3).text().strip()
                try:
                    pax_in = int(float(pax_in)) if pax_in else None
                except ValueError:
                    pax_in = None
                s.add(ChopperLog(section_id=sid, name=name, arrival=arrival, departure=departure, pax_in=pax_in))

            QMessageBox.information(self, "Saved", "Boat & chopper logs saved.")


class BoatsChopperModule(BaseModule):
    DISPLAY_NAME = "Boats & Chopper Log"

    def __init__(self, db, parent=None):
        super().__init__(db, parent)
        self.widget = BoatsChopperWidget(self.db)

    def get_widget(self) -> QWidget:
        return self.widget
