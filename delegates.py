
# =========================================
# file: nikan_drill_master/ui/widgets/delegates.py
# =========================================
from __future__ import annotations
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QModelIndex
from sqlalchemy.orm import Session
from models import CodeMain, CodeSub

class NPTRowColorDelegate(QStyledItemDelegate):
    """چرا: برجسته‌سازی ردیف‌های NPT در Time Log"""
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        is_npt = index.model().data(index.siblingAtColumn(6), Qt.DisplayRole)  # col 6 = NPT bool display
        if isinstance(is_npt, str):
            is_npt = is_npt.lower() in ("true", "1", "yes")
        if is_npt:
            option.backgroundBrush = QColor("#4E2A2A")

class CodeMainDelegate(QStyledItemDelegate):
    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session

    def createEditor(self, parent, option, index):
        cb = QComboBox(parent)
        cb.addItem("", None)
        for m in self.session.query(CodeMain).order_by(CodeMain.phase, CodeMain.code).all():
            cb.addItem(f"{m.phase} - {m.code} - {m.name}", m.id)
        return cb

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:
        val = index.data(Qt.EditRole)
        i = editor.findData(val)
        if i >= 0:
            editor.setCurrentIndex(i)

    def setModelData(self, editor: QComboBox, model, index) -> None:
        model.setData(index, editor.currentData(), Qt.EditRole)

class CodeSubDelegate(QStyledItemDelegate):
    def __init__(self, session: Session, main_code_col: int, parent=None):
        super().__init__(parent)
        self.session = session
        self.main_code_col = main_code_col

    def createEditor(self, parent, option, index):
        cb = QComboBox(parent)
        cb.addItem("", None)
        # main code id from sibling column
        main_id = index.model().data(index.siblingAtColumn(self.main_code_col), Qt.EditRole)
        if main_id:
            for s in self.session.query(CodeSub).filter(CodeSub.main_id == main_id).order_by(CodeSub.sub_code).all():
                cb.addItem(f"{s.sub_code} - {s.name}", s.id)
        return cb

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:
        val = index.data(Qt.EditRole)
        i = editor.findData(val)
        if i >= 0:
            editor.setCurrentIndex(i)

    def setModelData(self, editor: QComboBox, model, index) -> None:
        model.setData(index, editor.currentData(), Qt.EditRole)
