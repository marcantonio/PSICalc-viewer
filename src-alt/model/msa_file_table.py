from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal


class MsaFileTable(QAbstractTableModel):
    error = Signal(str, str, str)
    filesAdded = Signal(list, list)
    fileRemoved = Signal(int)

    def __init__(self):
        super().__init__()
        self.headers = ["Label", "Filename", "Apply alignment?", "Details", ""]
        self.files = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.files)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role):
        if not self.files:
            return None

        if role == Qt.DisplayRole:
            # Hide label for display if there's only 1 row
            if index.column() == 0 and self.rowCount() == 1:
                return ""
            return self.files[index.row()][index.column()]

        if role == Qt.EditRole:
            return self.files[index.row()][index.column()]

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            # Ensure label is valid before setting
            if index.column() == 0 and not self.isValidLabel(value, index.row()):
                return False
            self.files[index.row()][index.column()] = value
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
            self.files.insert(position, ["", "", "None", "", ""])
        self.endInsertRows()
        return True

    def removeRow(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        self.files.pop(row)
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
                existingFiles.add(file)
                existingLabels.add(label)
                newFiles.append(file)
                newLabels.append(label)

        if newFiles:
            self.filesAdded.emit(newFiles, newLabels)

    def removeFile(self, row):
        self.removeRow(row)
        self.fileRemoved.emit(row)

    # Generator to create labels A-Z, AA-ZZ, etc
    @staticmethod
    def labelGen():
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        labels = list(letters)
        while True:
            yield from labels
            labels = [a+b for a in labels for b in letters]
