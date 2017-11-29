#! coding: utf-8
import iso8601
from django.conf import settings
from django.test import TestCase
from nose.tools import raises

from series_tiempo_ar_api.apps.api.exceptions import CollapseError
from series_tiempo_ar_api.apps.api.models import Field
from series_tiempo_ar_api.apps.api.query.query import Query
from .helpers import get_series_id

SERIES_NAME = get_series_id('month')


class QueryTests(TestCase):
    single_series = SERIES_NAME

    @classmethod
    def setUpClass(cls):
        cls.field = Field.objects.get(series_id=cls.single_series)
        super(cls, QueryTests).setUpClass()

    def setUp(self):
        self.query = Query(index=settings.TEST_INDEX)

    def test_index_metadata_frequency(self):
        self.query.add_series(self.single_series, self.field)
        self.query.run()

        index_frequency = self.query.get_metadata()[0]['frequency']
        self.assertEqual(index_frequency, 'month')

    def test_index_metadata_start_end_dates(self):
        self.query.add_series(self.single_series, self.field)
        data = self.query.run()['data']

        index_meta = self.query.get_metadata()[0]
        self.assertEqual(data[0][0], index_meta['start_date'])
        self.assertEqual(data[-1][0], index_meta['end_date'])

    def test_collapse_index_metadata_frequency(self):
        collapse_interval = 'quarter'
        self.query.add_series(self.single_series, self.field)
        self.query.add_collapse(collapse=collapse_interval)
        self.query.run()

        index_frequency = self.query.get_metadata()[0]['frequency']
        self.assertEqual(index_frequency, collapse_interval)

    def test_collapse_index_metadata_start_end_dates(self):
        collapse_interval = 'quarter'
        self.query.add_series(self.single_series, self.field)
        self.query.add_collapse(collapse=collapse_interval)
        data = self.query.run()['data']

        index_meta = self.query.get_metadata()[0]
        self.assertEqual(data[0][0], index_meta['start_date'])
        self.assertEqual(data[-1][0], index_meta['end_date'])

    @raises(CollapseError)
    def test_invalid_collapse(self):
        collapse_interval = 'day'  # Serie cargada es mensual
        self.query.add_series(self.single_series, self.field)
        self.query.add_collapse(collapse=collapse_interval)

    def test_identifiers(self):

        self.query.add_series(self.single_series, self.field)
        # Devuelve lista de ids, una por serie. Me quedo con la primera (única)
        ids = self.query.get_series_identifiers()[0]
        field = Field.objects.get(series_id=self.single_series)
        self.assertEqual(ids['id'], field.series_id)
        self.assertEqual(ids['distribution'], field.distribution.identifier)
        self.assertEqual(ids['dataset'], field.distribution.dataset.identifier)

    def test_weekly_collapse(self):
        day_series_name = settings.TEST_SERIES_NAME.format('day')
        field = Field.objects.get(series_id=day_series_name)

        self.query.add_series(day_series_name, field)

        self.query.add_collapse(collapse='week')

        data = self.query.run()['data']

        first_date = iso8601.parse_date(data[0][0])
        second_date = iso8601.parse_date(data[1][0])

        delta = second_date - first_date
        self.assertEqual(delta.days, 7)

    def default_query_is_not_collapsed(self):
        self.assertEqual(False, self.query.has_collapse())

    def collapse_query_has_collapse(self):
        self.query.add_series(self.single_series, self.field)
        self.query.add_collapse()
        self.assertTrue(self.query.has_collapse(), True)
