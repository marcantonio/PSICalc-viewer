from PySide6.QtCore import QObject, Signal

import psicalc as pc


class MergedMsa(QObject):
    error = Signal(str, str, str)
    dataChanged = Signal()

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
        # The dataframes after applying settings. Always use these for output
        self.cookedDataframes = []
        # The merged MSA
        self.mergedMsa = None

    def addDataframe(self, label, dataframe):
        dataframe = dataframe.replace({'[-#?.]': None}, regex=True)
        self.labels.append(label)
        self.dataframes.append(dataframe)
        self.applyTransforms()

    def dropDataframe(self, idx):
        self.labels.pop(idx)
        self.dataframes.pop(idx)
        self.applyTransforms()

    # Returns dimensions and column names for existing dataframes
    def getDataFramesMetadata(self, idx):
        return (len(self.cookedDataframes[idx].columns), len(self.cookedDataframes[idx].index),
                self.cookedDataframes[idx].columns[0], self.cookedDataframes[idx].columns[-1])

    def setRowLabelingMethod(self, value):
        self.rowLabelingMethod = value
        self.applyTransforms()

    def setDurstonColumn(self, value):
        self.durstonColumn = value
        self.applyTransforms()

    def setInsertion(self, value):
        self.insertion = value
        self.applyTransforms()

    def setSpread(self, value):
        self.spread = value

    def setEntropyCutoff(self, value):
        self.entropyCutoff = value

    # Apply user settings to new data
    def applyTransforms(self):
        dataframes = self.dataframes.copy()
        if not dataframes:
            return

        if self.rowLabelingMethod == "deweese":
            dataframes = [pc.deweese_schema(df, "None") for df in dataframes]
        else:
            dataframes = [pc.durston_schema(df, self.durstonColumn) for df in dataframes]

        if self.insertion > 0:
            dataframes = self.removeInsertionData(dataframes)

        self.cookedDataframes = dataframes

        self.dataChanged.emit()

        # Only use the labels if there's more than one
        labels = self.labels if len(self.labels) > 1 else []

        self.mergedMsa = pc.merge_sequences(self.cookedDataframes, labels)

    def removeInsertionData(self, data):
        for i in range(len(data)):
            try:
                index_len = len(data[i].index)
                null_val = float(self.insertion) / 100
                data[i] = data[i].replace({'[-#?.]': None}, regex=True)
                labels_to_delete = []

                def series_remove_insertions(x):
                    non_nulls = x.count()
                    info_amount = non_nulls / index_len
                    if info_amount < null_val:
                        labels_to_delete.append(x.name)
                    return

                data[i].apply(series_remove_insertions, axis=0)
                data[i] = data[i].drop(labels_to_delete, axis=1)
            except IndexError or KeyError:
                self.error.emit("Error", "Not enough columns", None)

        return data

    def runClustering(self):
        results = pc.find_clusters(self.spread, self.mergedMsa, "pairwise", self.entropyCutoff)
        return results
