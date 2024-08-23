from PySide6.QtWidgets import (
    QTableView, QVBoxLayout, QPushButton, QWidget, QAbstractItemView, QHeaderView,
    QHBoxLayout, QStyledItemDelegate, QStyle, QComboBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QFont


class MsaTableView(QWidget):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model

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

        # Add the remove buttons to each row
        for i in range(self.model.rowCount()):
            self.add_remove_button(i)

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        # Add button
        add_button = QPushButton("Add file(s)...")
        add_button.clicked.connect(self.add_files)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Column sizes
        self.table.setColumnWidth(0, self.table.fontMetrics().horizontalAdvance(self.model._headers[0]) + 30)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(2, self.table.fontMetrics().horizontalAdvance(self.model._headers[2]) + 50)
        self.table.setColumnWidth(3, self.table.fontMetrics().horizontalAdvance("Sequences: XXXXX") + 50)
        self.table.setColumnWidth(4, 26)  # Image is 16px plus padding

        # Remove the dummy row used to calculate table height
        # TODO: Don't do this if real data is passed in
        self.remove_file(0)

    def add_remove_button(self, row):
        button = QPushButton()
        button.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        button.setStyleSheet("border: none;")
        button.clicked.connect(lambda _, row=row: self.remove_file(row))
        self.table.setIndexWidget(self.model.index(row, 4), button)

    def remove_file(self, row):
        self.model.beginRemoveRows(QModelIndex(), row, row)
        self.model._data.pop(row)
        self.model.endRemoveRows()
        # Re-add all buttons so the new indices are correct
        for i in range(self.model.rowCount()):
            self.add_remove_button(i)

    def add_files(self):
        files = QFileDialog.getOpenFileNames()[0]
        label_gen = MsaTableView.label_gen()
        existing_labels = {self.model.data(self.model.index(row, 0), Qt.EditRole) for row in range(self.model.rowCount())}
        existing_files = {self.model.data(self.model.index(row, 1), Qt.EditRole) for row in range(self.model.rowCount())}

        new_files = []
        new_labels = []
        for file in files:
            # Just skip files that already exist
            if file not in existing_files:
                label = next(label_gen)
                # Make sure labels are unique
                while label in existing_labels:
                    label = next(label_gen)

                self.model.insertRows(self.model.rowCount(), 1)
                row = self.model.rowCount() - 1
                self.model.setData(self.model.index(row, 0), label, Qt.EditRole)
                self.model.setData(self.model.index(row, 1), file, Qt.EditRole)
                self.add_remove_button(row)
                existing_files.add(file)
                existing_labels.add(label)
                new_files.append(file)
                new_labels.append(label)

        if new_files:
            self.model.importFiles(new_files, new_labels)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    # Generator to create labels A-Z, AA-ZZ, etc
    @staticmethod
    def label_gen():
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        labels = list(letters)
        while True:
            yield from labels
            labels = [a+b for a in labels for b in letters]


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
