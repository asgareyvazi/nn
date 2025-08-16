# File: ui/widgets/delegates.py
# Purpose: Item delegates for Table editing: ComboBoxDelegate, TimeEditDelegate, CheckBoxDelegate, and NPT row painter
# Next: modules/base.py

from PySide2.QtWidgets import QStyledItemDelegate, QComboBox, QTimeEdit
from PySide2.QtCore import Qt, QTime
from PySide2.QtGui import QColor, QBrush

class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items_provider_callable, parent=None):
        super().__init__(parent)
        self.items_provider = items_provider_callable

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        items = self.items_provider(index)
        for uid, txt in items:
            combo.addItem(txt, userData=uid)
        return combo

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        for i in range(editor.count()):
            if str(editor.itemData(i)) == str(value) or editor.itemText(i) == str(value):
                editor.setCurrentIndex(i); return

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentData(), Qt.EditRole)

class TimeEditDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        te = QTimeEdit(parent); te.setDisplayFormat("HH:mm:ss"); return te
    def setEditorData(self, editor, index):
        val = index.model().data(index, Qt.EditRole) or "00:00:00"
        parts = str(val).split(':')
        h = int(parts[0]) if parts and parts[0].isdigit() else 0
        m = int(parts[1]) if len(parts)>1 and parts[1].isdigit() else 0
        s = int(parts[2]) if len(parts)>2 and parts[2].isdigit() else 0
        editor.setTime(QTime(h, m, s))
    def setModelData(self, editor, model, index):
        model.setData(index, editor.time().toString("HH:mm:ss"), Qt.EditRole)

class CheckBoxDelegate(QStyledItemDelegate):
    # uses combobox style to avoid paint complexity
    def createEditor(self, parent, option, index):
        combo = QComboBox(parent); combo.addItem("No", False); combo.addItem("Yes", True); return combo
    def setEditorData(self, editor, index):
        val = index.model().data(index, Qt.EditRole)
        editor.setCurrentIndex(1 if val in (True, 'True', '1', 1) else 0)
    def setModelData(self, editor, model, index):
        model.setData(index, bool(editor.currentData()), Qt.EditRole)

class NPTRowPainter:
    @staticmethod
    def background_for(is_npt: bool):
        return QBrush(QColor(255, 230, 200)) if is_npt else QBrush(Qt.transparent)
