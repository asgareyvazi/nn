# File: modules/daily_report.py
# Purpose: Full TimeLogTableModel + DailyReportWidget (cascade Main->Sub, duration calculation, NPT coloring)
# Next: modules/well_info.py (to be delivered in next batch)

from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableView, QHBoxLayout, QDateEdit, QLabel, QMessageBox
from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex, QDate
from .base import BaseModule
from models import DailyReport, TimeLog, MainCode, SubCode
from ui.widgets.delegates import ComboBoxDelegate, TimeEditDelegate, CheckBoxDelegate, NPTRowPainter
from datetime import datetime

COL_FROM = 0; COL_TO = 1; COL_DURATION = 2; COL_MAIN = 3; COL_SUB = 4; COL_DESC = 5; COL_NPT = 6; COL_STATUS = 7

class TimeLogTableModel(QAbstractTableModel):
    HEADERS = ['From', 'To', 'Duration(min)', 'Main Code', 'Sub Code', 'Description', 'NPT', 'Status']
    def __init__(self, db, daily_report_id=None):
        super().__init__(); self.db=db; self.daily_report_id=daily_report_id; self.rows=[]
        if daily_report_id: self.load(daily_report_id)

    def load(self, daily_report_id):
        self.beginResetModel(); self.daily_report_id=daily_report_id
        with self.db.get_session() as s:
            self.rows = s.query(TimeLog).filter_by(daily_report_id=daily_report_id).order_by(TimeLog.id).all()
            for r in self.rows: _=r.main_code; _=r.sub_code
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()): return len(self.rows)
    def columnCount(self, parent=QModelIndex()): return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        tl = self.rows[index.row()]; c = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            return [
                tl.from_time or '', tl.to_time or '', tl.duration_minutes or 0,
                tl.main_phase_code_id or (tl.main_code.code if tl.main_code else ''),
                tl.sub_code_id or (tl.sub_code.code if tl.sub_code else ''),
                tl.description or '', bool(tl.is_npt), tl.status or ''
            ][c]
        if role == Qt.BackgroundRole and getattr(tl, 'is_npt', False):
            return NPTRowPainter.background_for(True)
        return None

    def headerData(self, s, o, r=Qt.DisplayRole):
        return self.HEADERS[s] if (r==Qt.DisplayRole and o==1) else None

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable if index.isValid() else Qt.ItemIsEnabled

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid(): return False
        r = index.row(); c = index.column(); tl = self.rows[r]
        with self.db.get_session() as s:
            obj = s.query(TimeLog).get(tl.id)
            if not obj: return False
            if c==COL_FROM: obj.from_time = str(value)
            elif c==COL_TO: obj.to_time = str(value)
            elif c==COL_DURATION:
                try: obj.duration_minutes = int(value)
                except: obj.duration_minutes = 0
            elif c==COL_MAIN:
                obj.main_phase_code_id = int(value) if value not in (None,'') else None
                if obj.sub_code_id:
                    sc = s.query(SubCode).get(obj.sub_code_id)
                    if sc and sc.main_code_id != obj.main_phase_code_id: obj.sub_code_id = None
            elif c==COL_SUB: obj.sub_code_id = int(value) if value not in (None,'') else None
            elif c==COL_DESC: obj.description = str(value)
            elif c==COL_NPT: obj.is_npt = bool(value)
            elif c==COL_STATUS: obj.status = str(value)
            # auto duration:
            try:
                if obj.from_time and obj.to_time:
                    fm = _to_minutes(obj.from_time); tm = _to_minutes(obj.to_time)
                    if tm < fm: tm += 24*60
                    obj.duration_minutes = max(0, tm - fm)
            except: pass
            s.flush(); refreshed = s.query(TimeLog).get(obj.id); self.rows[r] = refreshed
        self.dataChanged.emit(index, index)
        if c in (COL_FROM, COL_TO):
            self.dataChanged.emit(self.index(r, COL_DURATION), self.index(r, COL_DURATION))
        return True

    def insertRows(self, pos, rows=1, parent=QModelIndex()):
        self.beginInsertRows(QModelIndex(), pos, pos+rows-1)
        with self.db.get_session() as s:
            for _ in range(rows):
                tl = TimeLog(daily_report_id=self.daily_report_id, from_time='00:00:00', to_time='00:00:00', duration_minutes=0, is_npt=False, status='')
                s.add(tl); s.flush()
        self.load(self.daily_report_id); self.endInsertRows(); return True

    def removeRows(self, pos, rows=1, parent=QModelIndex()):
        if pos<0 or pos>=len(self.rows): return False
        self.beginRemoveRows(QModelIndex(), pos, pos+rows-1)
        ids=[self.rows[pos+i].id for i in range(rows) if pos+i < len(self.rows)]
        with self.db.get_session() as s:
            for i in ids:
                obj = s.query(TimeLog).get(i)
                if obj: s.delete(obj)
        self.load(self.daily_report_id); self.endRemoveRows(); return True

    def main_code_choices(self, index=None):
        with self.db.get_session() as s:
            rows = s.query(MainCode).order_by(MainCode.code).all()
        return [(r.id, f"{r.code} - {r.name}") for r in rows]

    def sub_code_choices_for_row(self, row_idx):
        if row_idx<0 or row_idx>=len(self.rows): return []
        main_id = self.rows[row_idx].main_phase_code_id
        if not main_id: return []
        with self.db.get_session() as s:
            subs = s.query(SubCode).filter_by(main_code_id=main_id).order_by(SubCode.code).all()
        return [(r.id, f"{r.code} - {r.name}") for r in subs]

def _to_minutes(s: str):
    try:
        h, m, *rest = s.split(':'); sec = int(rest[0]) if rest else 0
        return int(h)*60 + int(m) + (1 if sec>=30 else 0)
    except: return 0

class DailyReportWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self.current_report_id=None; self._build()

    def _build(self):
        v = QVBoxLayout(self)
        top = QHBoxLayout()
        self.date_edit = QDateEdit(); self.date_edit.setCalendarPopup(True); self.date_edit.setDate(QDate.currentDate())
        self.lbl_section = QLabel("Section: -")
        btn_load = QPushButton("Load Report"); btn_new = QPushButton("New Report")
        btn_save = QPushButton("Save Report"); btn_add = QPushButton("Add TimeLog"); btn_del = QPushButton("Delete Selected")
        for w in (self.lbl_section, self.date_edit, btn_load, btn_new, btn_save, btn_add, btn_del): top.addWidget(w)
        v.addLayout(top)

        self.table = QTableView(); v.addWidget(self.table)

        btn_new.clicked.connect(self._new_report)
        btn_load.clicked.connect(self._load_prompt)
        btn_save.clicked.connect(self._save_report)
        btn_add.clicked.connect(self._add_time_log)
        btn_del.clicked.connect(self._delete_selected)

    def _new_report(self):
        self.current_report_id=None; self.date_edit.setDate(QDate.currentDate()); self.lbl_section.setText("Section: -")

    def _load_prompt(self):
        QMessageBox.information(self, "Load", "Open a section from the left tree (double-click) to load/create today's report.")

    def load_daily_report(self, report_id):
        self.current_report_id = report_id
        with self.db.get_session() as s:
            dr = s.query(DailyReport).get(report_id)
            if not dr: return QMessageBox.warning(self, "Not found", "Daily report not found")
            self.date_edit.setDate(QDate(dr.report_date.year, dr.report_date.month, dr.report_date.day))
            self.lbl_section.setText(f"Section: {dr.section_id}")
        self.model = TimeLogTableModel(self.db, report_id)
        self.table.setModel(self.model)
        self.table.setItemDelegateForColumn(COL_FROM, TimeEditDelegate(self.table))
        self.table.setItemDelegateForColumn(COL_TO, TimeEditDelegate(self.table))
        self.table.setItemDelegateForColumn(COL_MAIN, ComboBoxDelegate(lambda idx: self.model.main_code_choices(idx), self.table))
        self.table.setItemDelegateForColumn(COL_SUB, ComboBoxDelegate(lambda idx: self.model.sub_code_choices_for_row(idx.row()), self.table))
        self.table.setItemDelegateForColumn(COL_NPT, CheckBoxDelegate(self.table))
        self.table.horizontalHeader().setStretchLastSection(True); self.table.resizeColumnsToContents()

    def _save_report(self):
        if not self.current_report_id: return QMessageBox.warning(self, "No report", "No report loaded")
        with self.db.get_session() as s:
            dr = s.query(DailyReport).get(self.current_report_id)
            if not dr: return QMessageBox.warning(self, "Error", "Report not found")
            qd = self.date_edit.date(); dr.report_date = qd.toPython()
        QMessageBox.information(self, "Saved", "Report metadata saved.")

    def _add_time_log(self):
        if not self.current_report_id: return QMessageBox.warning(self, "No report", "Load or create a report first")
        self.model.insertRows(self.model.rowCount(), 1)

    def _delete_selected(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel: return
        for r in sorted([i.row() for i in sel], reverse=True):
            self.model.removeRows(r, 1)

class DailyReportModule(BaseModule):
    DISPLAY_NAME = "Daily Report"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = DailyReportWidget(self.db)
    def get_widget(self): return self.widget
    def on_show(self, daily_report_id=None, section_id=None):
        if daily_report_id: return self.widget.load_daily_report(daily_report_id)
        if section_id:
            today = datetime.utcnow().date()
            with self.db.get_session() as s:
                dr = s.query(DailyReport).filter_by(section_id=section_id, report_date=today).first()
                if not dr:
                    dr = DailyReport(section_id=section_id, report_date=today); s.add(dr); s.flush()
                rid = dr.id
            self.widget.load_daily_report(rid)
