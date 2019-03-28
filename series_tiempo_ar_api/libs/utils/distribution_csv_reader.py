import urllib.parse

import pandas as pd


class DistributionCsvReader:

    def __init__(self, distribution, index_col):
        self.distribution = distribution
        self.index_col = index_col

    def read(self):
        url = self.distribution.download_url
        if url is None:
            raise ValueError

        # Fix a pandas fallando en lectura de URLs no ascii
        url = url.encode('UTF-8')
        url = urllib.parse.quote(url, safe='/:?=&')
        try:
            return self.read_csv_with_encoding(url, 'utf-8')
        except UnicodeDecodeError:
            return self.read_csv_with_encoding(url, 'latin1')

    def read_csv_with_encoding(self, url, encoding):
        return pd.read_csv(url,
                           parse_dates=[self.index_col],
                           index_col=self.index_col,
                           encoding=encoding)
