# File: ui/widgets/tree_view.py
# Purpose: Project tree (Company > Project > Well > Section). Emits selection signals.

from PySide2.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PySide2.QtCore import Signal

class ProjectTree(QWidget):
    open_daily_report = Signal(int)  # section_id

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Hierarchy"])
        self.tree.itemDoubleClicked.connect(self._on_dblclick)
        lay = QVBoxLayout(self)
        lay.addWidget(self.tree)
        self.reload()

    def reload(self):
        from models import Company, Project, Well, Section
        self.tree.clear()
        with self.db.get_session() as s:
            companies = s.query(Company).all()
            for c in companies:
                ci = QTreeWidgetItem([f"Company: {c.name}"])
                ci.setData(0, 32, ("company", c.id))
                self.tree.addTopLevelItem(ci)
                for p in c.projects:
                    pi = QTreeWidgetItem([f"Project: {p.name}"])
                    pi.setData(0, 32, ("project", p.id))
                    ci.addChild(pi)
                    for w in p.wells:
                        wi = QTreeWidgetItem([f"Well: {w.name}"])
                        wi.setData(0, 32, ("well", w.id))
                        pi.addChild(wi)
                        for sec in w.sections:
                            si = QTreeWidgetItem([f"Section: {sec.name}"])
                            si.setData(0, 32, ("section", sec.id))
                            wi.addChild(si)
        self.tree.expandAll()

    def _on_dblclick(self, item, col):
        kind, _id = item.data(0, 32) or (None, None)
        if kind == "section":
            self.open_daily_report.emit(_id)
