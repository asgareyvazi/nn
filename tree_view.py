
# =========================================
# file: nikan_drill_master/ui/widgets/tree_view.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt
from sqlalchemy.orm import Session
from models import Company, Project, Well, Section, DailyReport

class HierarchyTree(QWidget):
    """چرا: ناوبری سلسله‌مراتبی Company > Project > Well > Section > DailyReport"""
    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        lay = QVBoxLayout(self)
        lay.addWidget(self.tree)
        self.refresh()

    def refresh(self) -> None:
        self.tree.clear()
        for c in self.session.query(Company).order_by(Company.name).all():
            c_item = QTreeWidgetItem([c.name]); c_item.setData(0, Qt.UserRole, ("company", c.id))
            self.tree.addTopLevelItem(c_item)
            for p in c.projects:
                p_item = QTreeWidgetItem([p.name]); p_item.setData(0, Qt.UserRole, ("project", p.id))
                c_item.addChild(p_item)
                for w in p.wells:
                    w_item = QTreeWidgetItem([w.name]); w_item.setData(0, Qt.UserRole, ("well", w.id))
                    p_item.addChild(w_item)
                    for s in w.sections:
                        s_item = QTreeWidgetItem([s.name]); s_item.setData(0, Qt.UserRole, ("section", s.id))
                        w_item.addChild(s_item)
                        for dr in s.daily_reports:
                            d_item = QTreeWidgetItem([f"DR {dr.report_date.isoformat()}"]); d_item.setData(0, Qt.UserRole, ("daily_report", dr.id))
                            s_item.addChild(d_item)
        self.tree.expandToDepth(1)
