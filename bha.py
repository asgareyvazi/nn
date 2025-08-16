# File: modules/bha.py
# Purpose: BHA Runs table (multiple runs) with per-run tool list editor.

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QFormLayout
)
from .base import BaseModule
from models import Section, BHARun, BHATool
from datetime import datetime

class BHAWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        v = QVBoxLayout(self)
        self.cb_section=QComboBox(); v.addWidget(self.cb_section)
        top = QHBoxLayout(); v.addLayout(top)
        self.btn_new_run = QPushButton("New Run"); self.btn_delete_run=QPushButton("Delete Selected Run")
        top.addWidget(self.btn_new_run); top.addWidget(self.btn_delete_run)
        self.btn_new_run.clicked.connect(self._new_run); self.btn_delete_run.clicked.connect(self._del_run)

        self.tbl = QTableWidget(0,7)
        self.tbl.setHorizontalHeaderLabels(["RunID","Tool Type","OD(in)","ID(in)","Length(m)","Serial No","Weight(kg)"])
        v.addWidget(self.tbl)

        controls = QHBoxLayout()
        self.btn_add_tool=QPushButton("Add Tool Row"); self.btn_del_tool=QPushButton("Delete Tool Row"); self.btn_save=QPushButton("Save Tools")
        for b in (self.btn_add_tool,self.btn_del_tool,self.btn_save): controls.addWidget(b)
        v.addLayout(controls)
        self.btn_add_tool.clicked.connect(self._add_tool_row); self.btn_del_tool.clicked.connect(self._del_tool_row); self.btn_save.clicked.connect(self._save_tools)

        form = QFormLayout(); v.addLayout(form)
        self.le_run_label = QLineEdit(); form.addRow("Run Label (optional)", self.le_run_label)

        self.current_run_id=None
        self.cb_section.currentIndexChanged.connect(self._load_run)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _load_run(self):
        sid = self.cb_section.currentData(); self.current_run_id=None
        self.tbl.setRowCount(0)
        if sid is None: return
        with self.db.get_session() as s:
            run = s.query(BHARun).filter_by(section_id=sid).order_by(BHARun.id.desc()).first()
        if run:
            self.current_run_id=run.id; self.le_run_label.setText("")
            with self.db.get_session() as s:
                tools = s.query(BHATool).filter_by(run_id=run.id).all()
            for t in tools:
                r = self.tbl.rowCount(); self.tbl.insertRow(r)
                self.tbl.setItem(r,0,QTableWidgetItem(str(run.id)))
                self.tbl.setItem(r,1,QTableWidgetItem(t.tool_type or "")); self.tbl.setItem(r,2,QTableWidgetItem(str(t.od_in or 0)))
                self.tbl.setItem(r,3,QTableWidgetItem(str(t.id_in or 0))); self.tbl.setItem(r,4,QTableWidgetItem(str(t.length_m or 0)))
                self.tbl.setItem(r,5,QTableWidgetItem(t.serial_no or "")); self.tbl.setItem(r,6,QTableWidgetItem(str(t.weight_kg or 0)))

    def _new_run(self):
        sid = self.cb_section.currentData()
        if sid is None: return
        with self.db.get_session() as s:
            run = BHARun(section_id=sid); s.add(run); s.flush()
            self.current_run_id = run.id
        self.tbl.setRowCount(0)

    def _del_run(self):
        if self.current_run_id is None: return
        with self.db.get_session() as s:
            run = s.query(BHARun).get(self.current_run_id)
            if run: s.delete(run)
        self.current_run_id=None; self.tbl.setRowCount(0)

    def _add_tool_row(self):
        if self.current_run_id is None: return QMessageBox.warning(self, "No run", "Create a run first")
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        self.tbl.setItem(r,0,QTableWidgetItem(str(self.current_run_id)))
        for c in range(1,7): self.tbl.setItem(r, c, QTableWidgetItem(""))

    def _del_tool_row(self):
        sel = self.tbl.selectionModel().selectedRows()
        for r in sorted([i.row() for i in sel], reverse=True): self.tbl.removeRow(r)

    def _save_tools(self):
        if self.current_run_id is None: return
        with self.db.get_session() as s:
            # Clear and recreate
            for t in s.query(BHATool).filter_by(run_id=self.current_run_id).all(): s.delete(t)
            for r in range(self.tbl.rowCount()):
                def f(c):
                    try: return float(self.tbl.item(r,c).text())
                    except: return 0.0
                s.add(BHATool(
                    run_id=self.current_run_id,
                    tool_type=(self.tbl.item(r,1).text().strip() if self.tbl.item(r,1) else ''),
                    od_in=f(2), id_in=f(3), length_m=f(4),
                    serial_no=(self.tbl.item(r,5).text().strip() if self.tbl.item(r,5) else ''),
                    weight_kg=f(6), remarks="", run=self.le_run_label.text().strip() or None
                ))
        QMessageBox.information(self, "Saved", "BHA tools saved for current run.")

class BHAModule(BaseModule):
    DISPLAY_NAME = "BHA"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = BHAWidget(self.db)
    def get_widget(self): return self.widget
