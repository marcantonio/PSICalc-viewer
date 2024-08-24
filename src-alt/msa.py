class Msa:
    def __init__(self):
        # Clustering parameters
        self.entropyCutoff = 0.0
        self.rowLabelingMethod = "durston"
        self.durstonColumn = 0
        self.insertion = 0
        self.spread = 1
        # The raw dataframes as read from disk. Always use these when user settings change
        self.dataframes = []
        # The merged MSA
        self.mergedData = None

    def addDataframe(self, df):
        df = df.replace({'[-#?.]': None}, regex=True)
        self.dataframes.append(df)
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
