from PySide6.QtWidgets import (
    QTableView, QVBoxLayout, QPushButton, QWidget, QAbstractItemView, QHeaderView, QHBoxLayout,
    QStyledItemDelegate, QStyle, QComboBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtGui import QFont


# Adds a combo box to the alignment column
class AlignmentColumnDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        if index.column() == 2:
            editor = QComboBox(parent)
            editor.addItems(["None", "MUSCLE", "MAFFT"])
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            value = index.model().data(index, Qt.DisplayRole)
            editor.setCurrentText(value)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            model.setData(index, editor.currentText())
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


# Sets the cells' text to align top left
class TopLeftAlignDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignTop | Qt.AlignLeft
        super().paint(painter, option, index)


class MsaFiles(QAbstractTableModel):
    error = Signal(str, str)

    def __init__(self, data):
        super().__init__()
        self._headers = ["Label", "Filename", "Apply alignment?", "Details", ""]
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role):
        if not self._data:
            return None

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._data[index.row()][index.column()]

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            # Ensure label is valid before setting
            if index.column() == 0 and not self.is_valid_label(value, index.row()):
                return False
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def flags(self, index):
        default_flags = super().flags(index)
        # Make the label and alignment columns editable. Disable label for a single row
        if self.rowCount() > 1 and index.column() in [0, 2]:
            return default_flags | Qt.ItemIsEditable
        elif index.column() == 2:
            return default_flags | Qt.ItemIsEditable
        return default_flags

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]

    def insertRows(self, position, rows=1, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for _ in range(rows):
            self._data.insert(position, ["", "", "None", "", ""])
        self.endInsertRows()
        return True

    def is_valid_label(self, new_label, row):
        if not new_label:
            self.error.emit("Error", "Label cannot be blank")
            return False

        existing_labels = {self.data(self.index(r, 0), Qt.DisplayRole) for r in range(self.rowCount()) if r != row}
        if new_label in existing_labels:
            self.error.emit('Error', "Labels must be unique")
            return False

        return True


class MsaTableView(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        # Use the data passed or insert a dummy row to calculate the row height later
        if data:
            self.model = MsaFiles(data)
        else:
            self.model = MsaFiles([["", "", "None", "", ""]])

        # For errors from the model
        self.model.error.connect(self.show_error)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setShowGrid(False)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        # Fixed row height
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(60)

        # Larger font
        font = QFont()
        font.setPointSize(14)
        self.table.setFont(font)

        # Padding and a line between rows
        self.table.setStyleSheet("""
            QTableView::item {
                border-bottom: 1px solid lightgrey;
                padding: 5px;
            }
        """)

        # Make the alignment column a combo box
        self.table.setItemDelegateForColumn(2, AlignmentColumnDelegate(self.table))

        # Cell align text
        self.table.setItemDelegate(TopLeftAlignDelegate(self.table))

        # Two rows height. This works because a dummy row is inserted above
        self.table.setFixedHeight(self.table.verticalHeader().sectionSize(0) * 2 + self.table.horizontalHeader().height())

        for i in range(self.model.rowCount()):
            self.set_remove_button(i)

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        add_button = QPushButton("Add file(s)...")
        add_button.clicked.connect(self.add_files)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.table.setColumnWidth(0, self.table.fontMetrics().horizontalAdvance(self.model._headers[0]) + 30)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(2, self.table.fontMetrics().horizontalAdvance(self.model._headers[2]) + 50)
        self.table.setColumnWidth(3, self.table.fontMetrics().horizontalAdvance("Sequences: XXXXX") + 50)

        self.table.setColumnWidth(4, 16 + 10)

        # Remove the dummy row used to calculate table height
        self.remove_row(0)

    def set_remove_button(self, row):
        button = QPushButton()
        button.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        button.setStyleSheet("border: none;")
        button.clicked.connect(lambda _, row=row: self.remove_row(row))
        self.table.setIndexWidget(self.model.index(row, 4), button)

    def remove_row(self, row):
        self.model.beginRemoveRows(QModelIndex(), row, row)
        self.model._data.pop(row)
        self.model.endRemoveRows()
        for i in range(self.model.rowCount()):
            self.set_remove_button(i)

    def add_files(self):
        files = QFileDialog.getOpenFileNames()[0]
        label_gen = MsaTableView.label_gen()
        existing_labels = {self.model.data(self.model.index(row, 0), Qt.DisplayRole) for row in range(self.model.rowCount())}
        existing_files = {self.model.data(self.model.index(row, 1), Qt.DisplayRole) for row in range(self.model.rowCount())}

        for file in files:
            # Just skip files that already exist
            if file not in existing_files:
                # Make sure labels are unique
                label = next(label_gen)
                while label in existing_labels:
                    label = next(label_gen)

                self.model.insertRows(self.model.rowCount(), 1)
                self.model.setData(self.model.index(self.model.rowCount() - 1, 0), label, Qt.EditRole)
                self.model.setData(self.model.index(self.model.rowCount() - 1, 1), file, Qt.EditRole)
                self.set_remove_button(self.model.rowCount() - 1)

                existing_files.add(file)
                existing_labels.add(label)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    @staticmethod
    def label_gen():
        """
        Generator to create labels A-Z, AA-ZZ, etc
        """
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        labels = list(letters)
        while True:
            yield from labels
            labels = [a+b for a in labels for b in letters]
