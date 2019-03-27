import pandas as pd


class DistributionCsvReader:

    def __init__(self, distribution, index_col):
        self.distribution = distribution
        self.index_col = index_col

    def read(self):
        return pd.read_csv(self.distribution.download_url,
                           parse_dates=[self.index_col],
                           index_col=self.index_col)
