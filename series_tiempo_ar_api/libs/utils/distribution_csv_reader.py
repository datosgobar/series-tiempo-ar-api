from io import SEEK_SET

import pandas as pd


class DistributionCsvReader:

    def __init__(self, distribution, index_col):
        self.distribution = distribution
        self.index_col = index_col

    def read(self):
        data_file = self.distribution.data_file
        if data_file is None:
            raise ValueError

        try:
            return self.read_csv_with_encoding(data_file, 'utf-8')
        except UnicodeDecodeError:
            data_file.seek(SEEK_SET)
            return self.read_csv_with_encoding(self.distribution.data_file, 'latin1')

    def read_csv_with_encoding(self, data_file, encoding):
        return pd.read_csv(data_file,
                           parse_dates=[self.index_col],
                           index_col=self.index_col,
                           encoding=encoding)
