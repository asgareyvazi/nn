# ui/export_eowr_dialog.py
"""
Dialog to select well/project and options for End-of-Well export
"""

from PySide2.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget,
    QListWidgetItem, QPushButton, QFileDialog, QCheckBox, QMessageBox
)
from PySide2.QtCore import Qt
from database import Database
from models import Company, Project, Well, Section

class ExportEOWRDialog(QDialog):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Export End Of Well Report")
        self.resize(700, 420)
        self._build()
        self._load_wells()

    def _build(self):
        v = QVBoxLayout(self)
        hl = QHBoxLayout()
        hl.addWidget(QLabel("Well:"))
        self.cb_well = QComboBox(); hl.addWidget(self.cb_well)
        v.addLayout(hl)

        v.addWidget(QLabel("Select sections to include (leave empty to include all):"))
        self.lst_sections = QListWidget(); self.lst_sections.setSelectionMode(QListWidget.MultiSelection)
        v.addWidget(self.lst_sections)

        # format checkboxes
        fmt_h = QHBoxLayout()
        self.chk_docx = QCheckBox("DOCX"); self.chk_docx.setChecked(True)
        self.chk_pdf = QCheckBox("PDF")
        fmt_h.addWidget(QLabel("Output Format:")); fmt_h.addWidget(self.chk_docx); fmt_h.addWidget(self.chk_pdf)
        fmt_h.addStretch()
        v.addLayout(fmt_h)

        # buttons
        h2 = QHBoxLayout()
        self.btn_path = QPushButton("Choose Output Path"); self.lbl_path = QLabel("")
        h2.addWidget(self.btn_path); h2.addWidget(self.lbl_path)
        v.addLayout(h2)
        self.btn_export = QPushButton("Export"); self.btn_cancel = QPushButton("Cancel")
        btm = QHBoxLayout(); btm.addStretch(); btm.addWidget(self.btn_export); btm.addWidget(self.btn_cancel)
        v.addLayout(btm)

        # connect
        self.cb_well.currentIndexChanged.connect(self._load_sections)
        self.btn_path.clicked.connect(self._pick_path)
        self.btn_export.clicked.connect(self._on_export)
        self.btn_cancel.clicked.connect(self.reject)

        self._out_path = None

    def _load_wells(self):
        self.cb_well.clear()
        with self.db.get_session() as s:
            wells = s.query(Well).order_by(Well.name).all()
        for w in wells:
            self.cb_well.addItem(f"{w.name} ({w.rig_name or ''})", w.id)
        self._load_sections()

    def _load_sections(self):
        self.lst_sections.clear()
        wid = self.cb_well.currentData()
        if wid is None: return
        with self.db.get_session() as s:
            secs = s.query(Section).filter_by(well_id=wid).order_by(Section.name).all()
        for sc in secs:
            it = QListWidgetItem(f"{sc.name}"); it.setData(Qt.UserRole, sc.id)
            it.setCheckState(Qt.Unchecked)
            self.lst_sections.addItem(it)

    def _pick_path(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Report As", "eow_report.docx", "Word Document (*.docx);;PDF File (*.pdf)")
        if path:
            self._out_path = path
            self.lbl_path.setText(path)

    def _on_export(self):
        if not self._out_path:
            QMessageBox.warning(self, "Output", "Choose output path first")
            return
        if not (self.chk_docx.isChecked() or self.chk_pdf.isChecked()):
            QMessageBox.warning(self, "Format", "Select at least one format (DOCX or PDF)")
            return
        well_id = self.cb_well.currentData()
        sec_ids = []
        for i in range(self.lst_sections.count()):
            it = self.lst_sections.item(i)
            if it.checkState() == Qt.Checked:
                sec_ids.append(it.data(Qt.UserRole))
        # return values to caller via attributes
        self.result = {
            "well_id": well_id,
            "sections": sec_ids if sec_ids else None,
            "out_path": self._out_path,
            "docx": self.chk_docx.isChecked(),
            "pdf": self.chk_pdf.isChecked()
        }
        self.accept()
