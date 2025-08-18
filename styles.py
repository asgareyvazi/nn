
# =========================================
# file: nikan_drill_master/ui/styles.py
# =========================================
DARK = """
QWidget { background-color: #1E1F22; color: #E8E8EA; font-size: 12px; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit, QPlainTextEdit, QDateEdit, QTimeEdit, QDateTimeEdit {
    background-color: #2A2B2F; border: 1px solid #3A3B40; border-radius: 4px; padding: 4px;
}
QPushButton { background-color: #3A3B40; border: 1px solid #4A4B50; padding: 6px 10px; border-radius: 4px; }
QPushButton:hover { background-color: #4A4B50; }
QHeaderView::section { background-color: #2A2B2F; padding: 6px; border: none; }
QTreeView, QTableView { background-color: #222328; gridline-color: #3A3B40; selection-background-color: #29445E; }
QCheckBox::indicator { width: 16px; height: 16px; }
"""

LIGHT = """
QWidget { background-color: #F6F7FB; color: #1E1F22; font-size: 12px; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit, QPlainTextEdit, QDateEdit, QTimeEdit, QDateTimeEdit {
    background-color: #FFFFFF; border: 1px solid #D9D9DF; border-radius: 4px; padding: 4px;
}
QPushButton { background-color: #FFFFFF; border: 1px solid #D9D9DF; padding: 6px 10px; border-radius: 4px; }
QPushButton:hover { background-color: #EDEDF2; }
QHeaderView::section { background-color: #FFFFFF; padding: 6px; border: none; }
QTreeView, QTableView { background-color: #FFFFFF; gridline-color: #D9D9DF; selection-background-color: #D6E4FF; }
"""
