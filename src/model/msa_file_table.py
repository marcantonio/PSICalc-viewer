from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal

import psicalc as pc


class MsaFileTable(QAbstractTableModel):
    error = Signal(str, str, str)

    def __init__(self, msa):
        super().__init__()
        self.msa = msa
        self.msa.dataChanged.connect(lambda: self.layoutChanged.emit())
        self.headers = ["Label", "Filename", "Apply alignment?", "Details", ""]
        self.fileData = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.fileData)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role):
        if not self.fileData:
            return None

        if role == Qt.DisplayRole:
            # Hide labels if there is only one row
            if self.rowCount() == 1 and index.column() == 0:
                return ""

            # Build details column, omit label if one row
            if index.column() == 3:
                label = "" if self.rowCount() == 1 else self.fileData[index.row()][0]
                return self.buildDetails(index.row(), label)

            return self.fileData[index.row()][index.column()]

        if role == Qt.EditRole:
            return self.fileData[index.row()][index.column()]

        return None

    # Build the details string for `row`
    def buildDetails(self, row, label):
        try:
            (numColumns, numSequences, firstColumn, lastColumn) = self.msa.getDataFramesMetadata(row)
            labelRange = str(firstColumn) + "..." + str(lastColumn)
            return f"Columns: {numColumns}\nSequences: {numSequences}\nLabels: {labelRange}"
        except Exception:
            return "Error fetching details"

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            # Ensure label is valid before setting
            if index.column() == 0 and not self.isValidLabel(value, index.row()):
                return False
            self.fileData[index.row()][index.column()] = value
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

    def headerData(self, section, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def insertRows(self, position, rows=1, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for _ in range(rows):
            self.fileData.insert(position, ["", "", "None", "", ""])
        self.endInsertRows()
        return True

    def removeRow(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        self.fileData.pop(row)
        self.endRemoveRows()

    def getLabels(self, excludeRow=None):
        if excludeRow is None:
            return {self.data(self.index(row, 0), Qt.EditRole) for row in range(self.rowCount())}
        else:
            return {self.data(self.index(row, 0), Qt.EditRole) for row in range(self.rowCount()) if row != excludeRow}

    def getFiles(self):
        return {self.data(self.index(row, 1), Qt.EditRole) for row in range(self.rowCount())}

    def isValidLabel(self, newLabel, row):
        if not newLabel:
            self.error.emit("Error", "Label cannot be blank", None)
            return False

        existingLabels = self.getLabels(excludeRow=row)
        if newLabel in existingLabels:
            self.error.emit("Error", "Labels must be unique", None)
            return False

        return True

    def addFiles(self, files):
        labelGen = MsaFileTable.labelGen()
        existingLabels = self.getLabels()
        existingFiles = self.getFiles()

        for file in files:
            # Just skip files that already exist
            if file not in existingFiles:
                label = next(labelGen)
                # Make sure labels are unique
                while label in existingLabels:
                    label = next(labelGen)

                try:
                    self.importFile(file, label)
                except Exception as e:
                    self.error.emit("Error", f"Failed to read file \"{file}\"", str(e))
                    return

                self.insertRows(self.rowCount(), 1)
                row = self.rowCount() - 1
                self.setData(self.index(row, 0), label, Qt.EditRole)
                self.setData(self.index(row, 1), file, Qt.EditRole)
                existingFiles.add(file)
                existingLabels.add(label)

    def importFile(self, file, label):
        try:
            df = None
            if str(file).endswith((".txt", ".fasta")):
                df = pc.read_txt_file_format(file)
            else:
                df = pc.read_csv_file_format(file)
            self.msa.addDataframe(label, df)
        except Exception:
            raise

    def removeFile(self, row):
        self.removeRow(row)
        self.msa.dropDataframe(row)

    # Generator to create labels A-Z, AA-ZZ, etc
    @staticmethod
    def labelGen():
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        labels = list(letters)
        while True:
            yield from labels
            labels = [a+b for a in labels for b in letters]
