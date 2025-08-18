from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QTableWidgetItem, QMessageBox
from modules.base import ModuleBase
from database import session_scope
from models import DownholeEquipment, Section

class DownholeEquipmentModule(ModuleBase):
    def __init__(self, SessionLocal, parent=None):
        super().__init__(SessionLocal, parent)
        self._section_id: int | None = None
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        self.tbl = QTableWidget(0, 8)
        self.tbl.setHorizontalHeaderLabels(["Equipment Name","S/N","ID","Sliding Hrs","Cum Rotation","Cum Pumping","Cum Total Hrs","Remarks"])
        btns = QHBoxLayout()
        add = QPushButton("Add"); rm = QPushButton("Delete"); save = QPushButton("Save")
        add.clicked.connect(lambda: self.tbl.insertRow(self.tbl.rowCount()))
        rm.clicked.connect(lambda: self.tbl.removeRow(self.tbl.currentRow()))
        save.clicked.connect(self._save)
        btns.addWidget(add); btns.addWidget(rm); btns.addStretch(1); btns.addWidget(save)
        lay.addLayout(btns); lay.addWidget(self.tbl)

    def on_selection_changed(self, context: dict) -> None:
        sel = context.get("selection")
        if sel and sel[0] == "section":
            self._section_id = int(sel[1])

    def _save(self):
        if not self._section_id:
            QMessageBox.warning(self, "Selection", "Section را از درخت انتخاب کنید")
            return
        with session_scope(self.SessionLocal) as s:
            s.query(DownholeEquipment).filter(DownholeEquipment.section_id==self._section_id).delete()
            s.flush()
            for r in range(self.tbl.rowCount()):
                def gs(c):
                    return self.tbl.item(r,c).text() if self.tbl.item(r,c) else ""
                def gf(c):
                    try: return float(self.tbl.item(r,c).text())
                    except Exception: return None
                s.add(DownholeEquipment(
                    section_id=self._section_id,
                    equipment_name=gs(0),
                    serial_no=gs(1) or None,
                    tool_id=gs(2) or None,
                    sliding_hours=gf(3),
                    cum_rotation=gf(4),
                    cum_pumping=gf(5),
                    cum_total_hours=gf(6)
                ))
        QMessageBox.information(self, "Saved", "Downhole Equipment ذخیره شد")
