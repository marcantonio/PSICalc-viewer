from PySide6.QtWidgets import QTableView, QVBoxLayout, QPushButton, QWidget, QAbstractItemView, QHeaderView, QHBoxLayout, QStyledItemDelegate
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont


# Set the cells' text to align top left
class TopLeftAlignDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignTop | Qt.AlignLeft
        super().paint(painter, option, index)


class MsaFiles(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0])

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def headerData(self, section, orientation, role):
        headers = ["Label", "Filename", "Alignment", "Detail", "Remove"]
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return headers[section]

    def insertRows(self, position, rows=1, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for _ in range(rows):
            self._data.insert(position, ["", "", "", "", ""])
        self.endInsertRows()
        return True


class MsaTableView(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.model = MsaFiles(data)
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setShowGrid(False)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Fixed row height
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(50)

        # Larger font
        font = QFont()
        font.setPointSize(14)
        self.table.setFont(font)

        # Cell text alignment
        self.table.setItemDelegate(TopLeftAlignDelegate(self.table))

        # Two rows height
        self.table.setFixedHeight(self.table.verticalHeader().sectionSize(0) * 2 + self.table.horizontalHeader().height())

        for i in range(self.model.rowCount()):
            self.set_delete_button(i)

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_row)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    # Remove button for row
    def set_delete_button(self, row):
        button = QPushButton("Remove")
        button.clicked.connect(lambda _, row=row: self.remove_row(row))
        self.table.setIndexWidget(self.model.index(row, 4), button)

    def remove_row(self, row):
        self.model.beginRemoveRows(QModelIndex(), row, row)
        self.model._data.pop(row)
        self.model.endRemoveRows()
        for i in range(self.model.rowCount()):
            self.set_delete_button(i)

    def add_row(self):
        self.model.insertRows(self.model.rowCount(), 1)
        self.set_delete_button(self.model.rowCount() - 1)
