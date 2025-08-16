# File: modules/code_management.py
# Purpose: Full CRUD for MainCode and SubCode + helper API for other modules
# Next: modules/daily_report.py

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QMessageBox, QTableView, QComboBox
)
from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex
from .base import BaseModule
from models import MainCode, SubCode

class MainCodeTableModel(QAbstractTableModel):
    HEADERS = ['ID', 'Code', 'Name', 'Description']
    def __init__(self, db):
        super().__init__(); self.db = db; self.rows = []; self.load()
    def load(self):
        with self.db.get_session() as s:
            self.rows = s.query(MainCode).order_by(MainCode.code).all()
        self.layoutChanged.emit()
    def rowCount(self, parent=QModelIndex()): return len(self.rows)
    def columnCount(self, parent=QModelIndex()): return len(self.HEADERS)
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        mc = self.rows[index.row()]; c = index.column()
        if role == Qt.DisplayRole:
            return [mc.id, mc.code, mc.name, (mc.description or '')][:][c]
    def headerData(self, s, o, r=Qt.DisplayRole):
        return self.HEADERS[s] if (r==Qt.DisplayRole and o==1) else None

class SubCodeTableModel(QAbstractTableModel):
    HEADERS = ['ID', 'MainCode', 'Code', 'Name', 'Description']
    def __init__(self, db):
        super().__init__(); self.db = db; self.rows = []; self.load()
    def load(self):
        with self.db.get_session() as s:
            self.rows = s.query(SubCode).join(MainCode).order_by(MainCode.code, SubCode.code).all()
        self.layoutChanged.emit()
    def rowCount(self, parent=QModelIndex()): return len(self.rows)
    def columnCount(self, parent=QModelIndex()): return len(self.HEADERS)
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        sc = self.rows[index.row()]; c = index.column()
        if role == Qt.DisplayRole:
            if c==0: return sc.id
            if c==1: return sc.main_code.code if sc.main_code else ''
            if c==2: return sc.code
            if c==3: return sc.name
            if c==4: return sc.description or ''
    def headerData(self, s, o, r=Qt.DisplayRole):
        return self.HEADERS[s] if (r==Qt.DisplayRole and o==1) else None

class CodeManagementWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db
        self._build_ui(); self._load_models()

    def _build_ui(self):
        main = QVBoxLayout(self)

        # Main code form
        frm_main = QFormLayout()
        self.le_main_code = QLineEdit(); self.le_main_name = QLineEdit(); self.le_main_desc = QLineEdit()
        btn_add_main = QPushButton("Add Main Code"); btn_add_main.clicked.connect(self._add_main)
        frm_main.addRow("Main Code", self.le_main_code)
        frm_main.addRow("Name", self.le_main_name)
        frm_main.addRow("Description", self.le_main_desc)
        frm_main.addRow(btn_add_main)

        # Sub code form
        frm_sub = QFormLayout()
        self.cb_sub_main = QComboBox(); self.le_sub_code = QLineEdit(); self.le_sub_name = QLineEdit(); self.le_sub_desc = QLineEdit()
        btn_add_sub = QPushButton("Add Sub Code"); btn_add_sub.clicked.connect(self._add_sub)
        frm_sub.addRow("Parent Main", self.cb_sub_main)
        frm_sub.addRow("Sub Code", self.le_sub_code)
        frm_sub.addRow("Name", self.le_sub_name)
        frm_sub.addRow("Description", self.le_sub_desc)
        frm_sub.addRow(btn_add_sub)

        hl = QHBoxLayout(); hl.addLayout(frm_main); hl.addLayout(frm_sub)
        main.addLayout(hl)

        # Tables & actions
        self.tbl_main = QTableView(); self.tbl_sub = QTableView()
        btn_refresh = QPushButton("Refresh"); btn_refresh.clicked.connect(self._load_models)
        btn_delete_main = QPushButton("Delete Selected Main"); btn_delete_main.clicked.connect(self._delete_selected_main)
        btn_delete_sub = QPushButton("Delete Selected Sub"); btn_delete_sub.clicked.connect(self._delete_selected_sub)
        actions = QHBoxLayout(); actions.addWidget(btn_refresh); actions.addWidget(btn_delete_main); actions.addWidget(btn_delete_sub)
        main.addLayout(actions); main.addWidget(self.tbl_main); main.addWidget(self.tbl_sub)

    def _load_models(self):
        with self.db.get_session() as s:
            mains = s.query(MainCode).order_by(MainCode.code).all()
        self.cb_sub_main.clear()
        for m in mains: self.cb_sub_main.addItem(f"{m.code} - {m.name}", m.id)
        self.model_main = MainCodeTableModel(self.db)
        self.model_sub = SubCodeTableModel(self.db)
        self.tbl_main.setModel(self.model_main); self.tbl_sub.setModel(self.model_sub)

    def _add_main(self):
        code = self.le_main_code.text().strip(); name = self.le_main_name.text().strip(); desc = self.le_main_desc.text().strip()
        if not code or not name: return QMessageBox.warning(self, "Validation", "Main code and name required")
        with self.db.get_session() as s:
            if s.query(MainCode).filter_by(code=code).first():
                return QMessageBox.warning(self, "Exists", "Main code already exists")
            s.add(MainCode(code=code, name=name, description=desc))
        self.le_main_code.clear(); self.le_main_name.clear(); self.le_main_desc.clear(); self._load_models()

    def _add_sub(self):
        idx = self.cb_sub_main.currentIndex()
        if idx < 0: return QMessageBox.warning(self, "Validation", "Select parent main code")
        main_id = self.cb_sub_main.currentData()
        code = self.le_sub_code.text().strip(); name = self.le_sub_name.text().strip(); desc = self.le_sub_desc.text().strip()
        if not code or not name: return QMessageBox.warning(self, "Validation", "Sub code and name required")
        with self.db.get_session() as s:
            s.add(SubCode(main_code_id=main_id, code=code, name=name, description=desc))
        self.le_sub_code.clear(); self.le_sub_name.clear(); self.le_sub_desc.clear(); self._load_models()

    def _delete_selected_main(self):
        sel = self.tbl_main.selectionModel().selectedRows()
        if not sel: return QMessageBox.information(self, "Select", "Select a main row")
        mc = self.model_main.rows[sel[0].row()]
        with self.db.get_session() as s:
            obj = s.query(MainCode).get(mc.id)
            if obj: s.delete(obj)
        self._load_models()

    def _delete_selected_sub(self):
        sel = self.tbl_sub.selectionModel().selectedRows()
        if not sel: return QMessageBox.information(self, "Select", "Select a sub row")
        sc = self.model_sub.rows[sel[0].row()]
        with self.db.get_session() as s:
            obj = s.query(SubCode).get(sc.id)
            if obj: s.delete(obj)
        self._load_models()

class CodeManagementModule(BaseModule):
    DISPLAY_NAME = "Code Management"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = CodeManagementWidget(self.db)
    def get_widget(self): return self.widget
    def get_main_codes(self):
        with self.db.get_session() as s:
            return s.query(MainCode).order_by(MainCode.code).all()
    def get_sub_codes_for(self, main_code_id):
        with self.db.get_session() as s:
            return s.query(SubCode).filter_by(main_code_id=main_code_id).order_by(SubCode.code).all()
