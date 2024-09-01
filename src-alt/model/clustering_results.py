class ClusteringResults:
    def __init__(self, clusterMap, columnMap, lowEntropySites, mergedMsa):
        self.clusterMap = clusterMap
        self.columnMap = columnMap
        self.lowEntropySites = lowEntropySites
        self.mergedMsa = mergedMsa

    @classmethod
    def fromDict(cls, rDict):
        columnMap = rDict["column_map"]
        del rDict["column_map"]
        lowEntropySites = rDict["low_entropy_sites"]
        del rDict["low_entropy_sites"]
        mergedMsa = rDict["merged_msa"]
        del rDict["merged_msa"]
        return cls(rDict, columnMap, lowEntropySites, mergedMsa)
