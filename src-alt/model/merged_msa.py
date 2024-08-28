from PySide6.QtCore import QObject, Signal

import psicalc as pc


class MergedMsa(QObject):
    error = Signal(str, str, str)

    def __init__(self, data=[]):
        super().__init__()

        # Clustering parameters
        self.entropyCutoff = 0.0
        self.rowLabelingMethod = "durston"
        self.durstonColumn = 0
        self.insertion = 0
        self.spread = 1
        # Labels
        self.labels = []
        # The raw dataframes as read from disk. Always use these when user settings change
        self.dataframes = []
        # The merged MSA
        self.mergedData = None

    def addDataframe(self, label, dataframe):
        dataframe = dataframe.replace({'[-#?.]': None}, regex=True)
        self.labels.append(label)
        self.dataframes.append(dataframe)
        print(self.labels)
        print(len(self.dataframes))

    def dropDataframe(self, idx):
        self.labels.pop(idx)
        self.dataframes.pop(idx)
        print(self.labels)
        print(len(self.dataframes))

    def setRowLabelingMethod(self, value):
        self.rowLabelingMethod = value
        print(f"Row labeling method updated to: {self.rowLabelingMethod}")

    def setDurstonColumn(self, value):
        self.durstonColumn = value
        print(f"Durston column set to: {self.durstonColumn}")

    def setInsertion(self, value):
        self.insertion = value
        print(f"Insertion: {self.insertion}")

    def setSpread(self, value):
        self.spread = value
        print(f"Spread: {self.spread}")

    def setEntropyCutoff(self, value):
        self.entropyCutoff = value
        print(f"Entropy cutoff updated to: {self.entropyCutoff}")

    def importFiles(self, files, labels):
        if not files or not labels:
            return

        # Read all of the files and store in a list of dataframes
        for label, file in zip(labels, files):
            try:
                if str(file).endswith((".txt", ".fasta")):
                    df = pc.read_txt_file_format(file)
                else:
                    df = pc.read_csv_file_format(file)
                self.addDataframe(label, df)
            except Exception as e:
                self.error.emit("Error", f"Failed to read file {file}", str(e))
