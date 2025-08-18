from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout
)
from .base import BaseModule
from models import Formation

class FormationDataWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build()
        self._load_data()

    def _build(self):
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Name", "Lithology", "Top (MD)"])
        self.layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_del = QPushButton("Delete")
        self.btn_save = QPushButton("Save")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_del)
        btn_layout.addWidget(self.btn_save)
        self.layout.addLayout(btn_layout)

        self.btn_add.clicked.connect(self._add_row)
        self.btn_del.clicked.connect(self._delete_selected)
        self.btn_save.clicked.connect(self._save)

    def _load_data(self):
        self.table.setRowCount(0)
        with self.db.get_session() as session:
            formations = session.query(Formation).all()
            for formation in formations:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(formation.name or ""))
                self.table.setItem(row, 1, QTableWidgetItem(formation.lithology or ""))
                self.table.setItem(row, 2, QTableWidgetItem(str(formation.top_md or "")))

    def _add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col in range(3):
            self.table.setItem(row, col, QTableWidgetItem(""))

    def _delete_selected(self):
        for idx in sorted([i.row() for i in self.table.selectionModel().selectedRows()], reverse=True):
            self.table.removeRow(idx)

    def _save(self):
        with self.db.get_session() as session:
            session.query(Formation).delete()
            for row in range(self.table.rowCount()):
                name = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
                lithology = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                try:
                    top_md = float(self.table.item(row, 2).text()) if self.table.item(row, 2) else None
                except ValueError:
                    top_md = None
                if not name:
                    continue
                formation = Formation(name=name, lithology=lithology, top_md=top_md)
                session.add(formation)
        QMessageBox.information(self, "Saved", "Formation data saved successfully.")

class FormationDataModule(BaseModule):
    DISPLAY_NAME = "Formation Data"

    def __init__(self, db, parent=None):
        super().__init__(db, parent)
        self.widget = FormationDataWidget(self.db)

    def get_widget(self):
        return self.widget
