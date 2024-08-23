class Msa:
    def __init__(self):
        # The raw dataframes as read from disk. Always use these when user settings change
        self.dataframes = []
        # The merged MSA
        self.merged_data = None

    def add_dataframe(self, df):
        df = df.replace({'[-#?.]': None}, regex=True)
        self.dataframes.append(df)
        print(len(self.dataframes))
