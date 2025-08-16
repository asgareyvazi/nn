# File: modules/material_handling.py
# Purpose: Material handling notes + requests per section.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QTextEdit, QPushButton, QComboBox, QMessageBox
from .base import BaseModule
from models import Section, MaterialNote

class MaterialHandlingWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self._build(); self._load_sections()

    def _build(self):
        self.l = QVBoxLayout(self)
        self.cb_section = QComboBox(); self.l.addWidget(self.cb_section)
        self.notes = [QTextEdit() for _ in range(6)]
        for i, t in enumerate(self.notes): self.l.addWidget(t)
        self.btn_save = QPushButton("Save"); self.btn_save.clicked.connect(self._save); self.l.addWidget(self.btn_save)
        self.cb_section.currentIndexChanged.connect(self._load)

    def _load_sections(self):
        self.cb_section.clear()
        with self.db.get_session() as s:
            rows = s.query(Section).all()
        for r in rows: self.cb_section.addItem(f"{r.id} - {r.name}", r.id)

    def _load(self):
        sid = self.cb_section.currentData()
        for t in self.notes: t.clear()
        if sid is None: return
        with self.db.get_session() as s:
            rows = s.query(MaterialNote).filter_by(section_id=sid).order_by(MaterialNote.note_no).all()
        for r in rows:
            if 1 <= r.note_no <= 6:
                self.notes[r.note_no - 1].setPlainText(r.text or "")

    def _save(self):
        sid = self.cb_section.currentData(); 
        if sid is None: return
        with self.db.get_session() as s:
            for rec in s.query(MaterialNote).filter_by(section_id=sid).all(): s.delete(rec)
            for i, t in enumerate(self.notes, start=1):
                txt = t.toPlainText().strip()
                if not txt: continue
                s.add(MaterialNote(section_id=sid, note_no=i, text=txt))
        QMessageBox.information(self, "Saved", "Material notes saved.")

class MaterialHandlingModule(BaseModule):
    DISPLAY_NAME = "Material Handling"
    def __init__(self, db, parent=None):
        super().__init__(db, parent); self.widget = MaterialHandlingWidget(self.db)
    def get_widget(self): return self.widget
