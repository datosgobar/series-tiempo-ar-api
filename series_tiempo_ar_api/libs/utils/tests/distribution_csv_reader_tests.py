import os
from django.test import TestCase

from mock import Mock
from nose.tools import raises

from series_tiempo_ar_api.libs.utils.distribution_csv_reader import DistributionCsvReader

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class DistributionCsvReaderTests(TestCase):

    def test_reader_returns_time_series_data_frame(self):
        distribution = Mock(download_url=os.path.join(SAMPLES_DIR, 'daily_periodicity.csv'))
        index_col = 'indice_tiempo'
        data_frame = DistributionCsvReader(distribution, index_col).read()

        self.assertListEqual(list(data_frame.columns), ['tasas_interes_call', 'tasas_interes_badlar', 'tasas_interes_pm'])

    @raises(ValueError)
    def test_validate_distribution_empty_url(self):
        distribution = Mock(download_url=None)

        index_col = 'indice_tiempo'
        DistributionCsvReader(distribution, index_col).read()
