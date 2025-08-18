
# =========================================
# file: nikan_drill_master/modules/code_management.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QTextEdit, QMessageBox
from sqlalchemy.orm import Session
from database import session_scope
from modules.base import ModuleBase
from models import CodeMain, CodeSub

class CodeManagementModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        # Main codes table
        self.tbl_main = QTableWidget(0, 4)
        self.tbl_main.setHorizontalHeaderLabels(["Phase", "Code", "Name", "Description"])
        # Sub codes table
        self.tbl_sub = QTableWidget(0, 4)
        self.tbl_sub.setHorizontalHeaderLabels(["Main Code ID", "Sub-Code", "Name", "Description"])

        btns = QHBoxLayout()
        btn_add_main = QPushButton("Add Main"); btn_del_main = QPushButton("Delete Main")
        btn_add_sub = QPushButton("Add Sub"); btn_del_sub = QPushButton("Delete Sub")
        btn_save = QPushButton("Save All")

        btn_add_main.clicked.connect(self._add_main)
        btn_del_main.clicked.connect(self._del_main)
        btn_add_sub.clicked.connect(self._add_sub)
        btn_del_sub.clicked.connect(self._del_sub)
        btn_save.clicked.connect(self._save)

        btns.addWidget(btn_add_main); btns.addWidget(btn_del_main)
        btns.addWidget(btn_add_sub); btns.addWidget(btn_del_sub)
        btns.addStretch(1); btns.addWidget(btn_save)

        lay.addLayout(btns)
        lay.addWidget(self.tbl_main)
        lay.addWidget(self.tbl_sub)

    def refresh(self):
        with session_scope(self.SessionLocal) as s:
            mains = s.query(CodeMain).order_by(CodeMain.phase, CodeMain.code).all()
            subs = s.query(CodeSub).order_by(CodeSub.main_id, CodeSub.sub_code).all()

        self.tbl_main.setRowCount(0)
        for m in mains:
            r = self.tbl_main.rowCount(); self.tbl_main.insertRow(r)
            self.tbl_main.setItem(r, 0, QTableWidgetItem(m.phase))
            self.tbl_main.setItem(r, 1, QTableWidgetItem(m.code))
            self.tbl_main.setItem(r, 2, QTableWidgetItem(m.name))
            self.tbl_main.setItem(r, 3, QTableWidgetItem(m.description or ""))

        self.tbl_sub.setRowCount(0)
        for s in subs:
            r = self.tbl_sub.rowCount(); self.tbl_sub.insertRow(r)
            self.tbl_sub.setItem(r, 0, QTableWidgetItem(str(s.main_id)))
            self.tbl_sub.setItem(r, 1, QTableWidgetItem(s.sub_code))
            self.tbl_sub.setItem(r, 2, QTableWidgetItem(s.name))
            self.tbl_sub.setItem(r, 3, QTableWidgetItem(s.description or ""))

    def _add_main(self):
        r = self.tbl_main.rowCount(); self.tbl_main.insertRow(r)

    def _del_main(self):
        r = self.tbl_main.currentRow()
        if r < 0: return
        phase = self.tbl_main.item(r, 0).text() if self.tbl_main.item(r, 0) else ""
        code = self.tbl_main.item(r, 1).text() if self.tbl_main.item(r, 1) else ""
        with session_scope(self.SessionLocal) as s:
            m = s.query(CodeMain).filter(CodeMain.phase==phase, CodeMain.code==code).one_or_none()
            if m: s.delete(m)
        self.refresh()

    def _add_sub(self):
        r = self.tbl_sub.rowCount(); self.tbl_sub.insertRow(r)

    def _del_sub(self):
        r = self.tbl_sub.currentRow()
        if r < 0: return
        try:
            main_id = int(self.tbl_sub.item(r, 0).text())
        except Exception:
            main_id = -1
        sub_code = self.tbl_sub.item(r, 1).text() if self.tbl_sub.item(r, 1) else ""
        with session_scope(self.SessionLocal) as s:
            sub = s.query(CodeSub).filter(CodeSub.main_id==main_id, CodeSub.sub_code==sub_code).one_or_none()
            if sub: s.delete(sub)
        self.refresh()

    def _save(self):
        with session_scope(self.SessionLocal) as s:
            s.query(CodeSub).delete()
            s.query(CodeMain).delete()
            s.flush()
            for r in range(self.tbl_main.rowCount()):
                phase = (self.tbl_main.item(r, 0).text() if self.tbl_main.item(r,0) else "").strip()
                code = (self.tbl_main.item(r, 1).text() if self.tbl_main.item(r,1) else "").strip()
                name = (self.tbl_main.item(r, 2).text() if self.tbl_main.item(r,2) else "").strip()
                desc = (self.tbl_main.item(r, 3).text() if self.tbl_main.item(r,3) else "").strip() or None
                if phase and code and name:
                    s.add(CodeMain(phase=phase, code=code, name=name, description=desc))
            s.flush()
            for r in range(self.tbl_sub.rowCount()):
                try:
                    main_id = int(self.tbl_sub.item(r, 0).text())
                except Exception:
                    main_id = None
                sub_code = (self.tbl_sub.item(r, 1).text() if self.tbl_sub.item(r,1) else "").strip()
                name = (self.tbl_sub.item(r, 2).text() if self.tbl_sub.item(r,2) else "").strip()
                desc = (self.tbl_sub.item(r, 3).text() if self.tbl_sub.item(r,3) else "").strip() or None
                if main_id and sub_code and name:
                    s.add(CodeSub(main_id=main_id, sub_code=sub_code, name=name, description=desc))
        QMessageBox.information(self, "Saved", "Codes ذخیره شد")
        self.refresh()
