from PySide6.QtWidgets import (
    QTableView, QVBoxLayout, QPushButton, QWidget, QAbstractItemView, QHeaderView,
    QHBoxLayout, QStyledItemDelegate, QStyle, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class MsaTableView(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model

        # Insert and remove a dummy row to calculate table height
        self.model.insertRow(0)
        self.initUI()
        self.model.removeRow(0)

        # Respond to the model
        self.model.rowsInserted.connect(self.rowsUpdated)
        self.model.rowsRemoved.connect(self.rowsUpdated)

    def initUI(self):
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
        for row in range(self.model.rowCount()):
            self.addRemoveButton(row)

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        # Add button
        addButton = QPushButton("Add file(s)...")
        addButton.clicked.connect(self.addFiles)
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(addButton)

        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        # Column sizes
        self.table.setColumnWidth(0, self.table.fontMetrics().horizontalAdvance(self.model.headerData(0)) + 30)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(2, self.table.fontMetrics().horizontalAdvance(self.model.headerData(2)) + 50)
        self.table.setColumnWidth(3, self.table.fontMetrics().horizontalAdvance("Sequences: XXXXX") + 50)  # Some dummy text
        self.table.setColumnWidth(4, 26)  # Image is 16px plus padding

    def addRemoveButton(self, row):
        button = QPushButton()
        button.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        button.setStyleSheet("border: none;")
        button.clicked.connect(lambda _, row=row: self.model.removeFile(row))
        self.table.setIndexWidget(self.model.index(row, 4), button)

    def addFiles(self):
        files = QFileDialog.getOpenFileNames()[0]
        self.model.addFiles(files)

    # Signaled changes from the model
    def rowsUpdated(self, parent, first, last):
        # Re-add all buttons so the new indices are correct
        for i in range(self.model.rowCount()):
            self.addRemoveButton(i)


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
