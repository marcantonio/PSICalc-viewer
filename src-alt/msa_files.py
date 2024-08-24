from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal

from msa import Msa
import psicalc as pc


class MsaFiles(QAbstractTableModel):
    error = Signal(str, str)

    def __init__(self, data=[]):
        super().__init__()
        self.msa = Msa()
        self._headers = ["Label", "Filename", "Apply alignment?", "Details", ""]
        self._data = data

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
        defaultFlags = super().flags(index)
        # Don't allow label to be edited when only 1 row is present
        if index.column() == 0 and self.rowCount() == 1:
            return defaultFlags
        # Make the label and alignment columns editable
        elif index.column() in [0, 2]:
            return defaultFlags | Qt.ItemIsEditable
        return defaultFlags

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

    def isValidLabel(self, newLabel, row):
        if not newLabel:
            self.error.emit("Error", "Label cannot be blank")
            return False

        existingLabels = {self.data(self.index(r, 0), Qt.EditRole) for r in range(self.rowCount()) if r != row}
        if newLabel in existingLabels:
            self.error.emit('Error', "Labels must be unique")
            return False

        return True

    def addFiles(self, files):
        labelGen = MsaFiles.labelGen()
        existingLabels = {self.data(self.index(row, 0), Qt.EditRole) for row in range(self.rowCount())}
        existingFiles = {self.data(self.index(row, 1), Qt.EditRole) for row in range(self.rowCount())}

        newFiles = []
        newLabels = []
        for file in files:
            # Just skip files that already exist
            if file not in existingFiles:
                label = next(labelGen)
                # Make sure labels are unique
                while label in existingLabels:
                    label = next(labelGen)

                self.insertRows(self.rowCount(), 1)
                row = self.rowCount() - 1
                self.setData(self.index(row, 0), label, Qt.EditRole)
                self.setData(self.index(row, 1), file, Qt.EditRole)
                #self.addRemoveButton(row)
                existingFiles.add(file)
                existingLabels.add(label)
                newFiles.append(file)
                newLabels.append(label)

        if newFiles:
            self.importFiles(newFiles, newLabels)

    def removeFile(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        self._data.pop(row)
        self.endRemoveRows()

    def importFiles(self, files, labels):
        if not files or not labels:
            return

        # Read all of the files and store in a list of dataframes
        for file in files:
            if str(file).endswith((".txt", ".fasta")):
                df = pc.read_txt_file_format(file)
            else:
                df = pc.read_csv_file_format(file)

            self.msa.addDataframe(df)

    # Generator to create labels A-Z, AA-ZZ, etc
    @staticmethod
    def labelGen():
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        labels = list(letters)
        while True:
            yield from labels
            labels = [a+b for a in labels for b in letters]
