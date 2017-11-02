#! coding: utf-8
from django.test import TestCase
from nose.tools import raises

from series_tiempo_ar_api.apps.api.query.exceptions import CollapseError
from series_tiempo_ar_api.apps.api.query.query import Query


class QueryTests(TestCase):
    single_series = 'random-0'

    def setUp(self):
        self.query = Query()

    def test_index_metadata_frequency(self):
        self.query.add_series(self.single_series)
        self.query.run()

        index_frequency = self.query.get_metadata()[0]['frequency']
        self.assertEqual(index_frequency, 'month')

    def test_index_metadata_start_end_dates(self):
        self.query.add_series(self.single_series)
        self.query.run()

        index_meta = self.query.get_metadata()[0]
        self.assertEqual(self.query.data[0][0], index_meta['start_date'])
        self.assertEqual(self.query.data[-1][0], index_meta['end_date'])

    def test_collapse_index_metadata_frequency(self):
        collapse_interval = 'quarter'
        self.query.add_series(self.single_series)
        self.query.add_collapse(collapse=collapse_interval)
        self.query.run()

        index_frequency = self.query.get_metadata()[0]['frequency']
        self.assertEqual(index_frequency, collapse_interval)

    def test_collapse_index_metadata_start_end_dates(self):
        collapse_interval = 'quarter'
        self.query.add_series(self.single_series)
        self.query.add_collapse(collapse=collapse_interval)
        self.query.run()

        index_meta = self.query.get_metadata()[0]
        self.assertEqual(self.query.data[0][0], index_meta['start_date'])
        self.assertEqual(self.query.data[-1][0], index_meta['end_date'])

    @raises(CollapseError)
    def test_invalid_collapse(self):
        collapse_interval = 'day'  # Serie cargada es mensual
        self.query.add_series(self.single_series)
        self.query.add_collapse(collapse=collapse_interval)
