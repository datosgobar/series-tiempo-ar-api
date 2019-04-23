import os

from django.test import TestCase

from mock import Mock
from nose.tools import raises

from series_tiempo_ar_api.libs.utils.distribution_csv_reader import DistributionCsvReader

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class DistributionCsvReaderTests(TestCase):

    def test_reader_returns_time_series_data_frame(self):
        distribution = Mock(data_file=open(os.path.join(SAMPLES_DIR, 'daily_periodicity.csv')))
        index_col = 'indice_tiempo'
        data_frame = DistributionCsvReader(distribution, index_col).read()

        series = ['tasas_interes_call', 'tasas_interes_badlar', 'tasas_interes_pm']
        self.assertListEqual(list(data_frame.columns), series)

    @raises(ValueError)
    def test_validate_distribution_empty_url(self):
        distribution = Mock(data_file=None)

        index_col = 'indice_tiempo'
        DistributionCsvReader(distribution, index_col).read()

    def test_read_utf8_distribution(self):
        distribution = Mock(data_file=open(os.path.join(SAMPLES_DIR, 'daily_periodicity_utf8.csv')))
        index_col = 'índice_tiempo'
        data_frame = DistributionCsvReader(distribution, index_col).read()

        series = ['tasas_interés_call', 'tasas_interés_badlar', 'tasas_interés_pm']
        self.assertListEqual(list(data_frame.columns), series)

    def test_read_latin1_distribution(self):
        distribution = Mock(data_file=open(os.path.join(SAMPLES_DIR, 'daily_periodicity_latin1.csv'), encoding='latin-1'))
        index_col = 'índice_tiempo'
        data_frame = DistributionCsvReader(distribution, index_col).read()

        series = ['tasas_interés_call', 'tasas_interés_badlar', 'tasas_interés_pm']
        self.assertListEqual(list(data_frame.columns), series)
