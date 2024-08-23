from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal

from msa import Msa
import psicalc as pc


class MsaFiles(QAbstractTableModel):
    error = Signal(str, str)

    def __init__(self, data=[]):
        super().__init__()
        self.msa = Msa()
        self._headers = ["Label", "Filename", "Apply alignment?", "Details", ""]
        if data:
            self._data = data
        else:
            # If not data, start with a dummy row to calculate the row height
            self._data = [["", "", "None", "", ""]]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role):
        if not self._data:
            return None

        if role == Qt.DisplayRole:
            # Hide label for display if there's only 1 row
            if index.column() == 0 and self.rowCount() == 1:
                return ""
            return self._data[index.row()][index.column()]

        if role == Qt.EditRole:
            return self._data[index.row()][index.column()]

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            # Ensure label is valid before setting
            if index.column() == 0 and not self.isValidLabel(value, index.row()):
                return False
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def flags(self, index):
        default_flags = super().flags(index)
        # Don't allow label to be edited when only 1 row is present
        if index.column() == 0 and self.rowCount() == 1:
            return default_flags
        # Make the label and alignment columns editable
        elif index.column() in [0, 2]:
            return default_flags | Qt.ItemIsEditable
        return default_flags

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

    def insertRows(self, position, rows=1, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for _ in range(rows):
            self._data.insert(position, ["", "", "None", "", ""])
        self.endInsertRows()
        return True

    def isValidLabel(self, new_label, row):
        if not new_label:
            self.error.emit("Error", "Label cannot be blank")
            return False

        existing_labels = {self.data(self.index(r, 0), Qt.EditRole) for r in range(self.rowCount()) if r != row}
        if new_label in existing_labels:
            self.error.emit('Error', "Labels must be unique")
            return False

        return True

    def importFiles(self, files, labels):
        print(files)
        if not files or not labels:
            return

        # Read all of the files and store in a list of dataframes
        for file in files:
            if str(file).endswith((".txt", ".fasta")):
                df = pc.read_txt_file_format(file)
            else:
                df = pc.read_csv_file_format(file)

            self.msa.add_dataframe(df)
