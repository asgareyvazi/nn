# File: ui/main_window.py
# Purpose: Main window with Ribbon, ProjectTree, and a central stacked module area. Hooks modules by name.

from PySide2.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QMessageBox
from PySide2.QtCore import Qt
from ui.widgets.ribbon import Ribbon
from ui.widgets.tree_view import ProjectTree
from modules.daily_report import DailyReportModule
from modules.code_management import CodeManagementModule
from modules.base import BaseModule

# Import more modules progressively (will be defined in next parts)
# from modules.well_info import WellInfoModule
# ... (others will be added when provided)

class MainWindow(QMainWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Nikan Drill Master")
        self.resize(1300, 800)

        self.ribbon = Ribbon(self)
        self.setMenuWidget(self.ribbon)

        self.tree = ProjectTree(self.db, self)
        self.stack = QStackedWidget(self)

        central = QWidget(self)
        lay = QHBoxLayout(central)
        lay.addWidget(self.tree, 2)
        lay.addWidget(self.stack, 5)
        self.setCentralWidget(central)

        self.modules = {}
        self._build_modules()
        self._wire()

    def _build_modules(self):
        # Core modules available now
        self.add_module("Daily Report", DailyReportModule(self.db))
        self.add_module("Code Management", CodeManagementModule(self.db))
        # Placeholders for menu (will be connected later as we deliver them)
        self.ribbon.add_group("Home", [
            ("Well Info", self._todo),
            ("Supervisor Signature", self._todo),
            ("Preferences", self._todo),
        ])
        self.ribbon.add_group("Daily Ops", [
            ("Daily Report", lambda: self.show_module("Daily Report")),
            ("Work Summary", self._todo),
            ("Alerts", self._todo),
        ])
        self.ribbon.add_group("Planning", [
            ("Code Management", lambda: self.show_module("Code Management")),
            ("Seven Days Lookahead", self._todo),
            ("NPT Report", self._todo),
        ])
        self.ribbon.add_group("Export", [
            ("Export Center", self._todo),
        ])

    def _todo(self):
        QMessageBox.information(self, "Coming up", "This module is coming in the next batches.")

    def add_module(self, name: str, module: BaseModule):
        self.modules[name] = module
        self.stack.addWidget(module.get_widget())

    def show_module(self, name: str):
        mod = self.modules.get(name)
        if not mod:
            QMessageBox.warning(self, "Not found", f"Module {name} not registered")
            return
        self.stack.setCurrentWidget(mod.get_widget())
        if hasattr(mod, "on_show"):
            mod.on_show()

    def _wire(self):
        self.tree.open_daily_report.connect(self._open_section_daily)

    def _open_section_daily(self, section_id: int):
        # ensure the Daily Report module opens the right section/date
        self.show_module("Daily Report")
        mod = self.modules["Daily Report"]
        mod.on_show(section_id=section_id)
