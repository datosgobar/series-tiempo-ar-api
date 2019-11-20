#! coding: utf-8
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from iso8601 import iso8601

from django_datajsonar.models import Field, Catalog
from series_tiempo_ar_api.apps.api.query.pipeline import DateFilter
from series_tiempo_ar_api.apps.api.query.query import Query
from ..helpers import get_series_id, setup_database

SERIES_NAME = get_series_id('month')


class DateFilterTests(TestCase):
    single_series = SERIES_NAME

    start_date = '2001-01-01'
    end_date = '2005-01-01'

    def setUp(self):
        self.query = Query()
        self.cmd = DateFilter()

    @classmethod
    def setUpTestData(cls):
        if not Catalog.objects.count():
            setup_database()

        cls.field = Field.objects.get(identifier=cls.single_series)

    def test_start_date(self):
        self.query.add_series(self.field, 'value')
        self.cmd.run(self.query, {'start_date': self.start_date})
        self.query.sort('asc')

        data = self.query.run()['data']

        first_timestamp = data[0][0]
        self.assertEqual(self.start_date, first_timestamp)

    def test_end_date(self):
        self.query.add_series(self.field, 'value')
        self.cmd.run(self.query, {'end_date': self.end_date})
        self.query.sort('asc')
        # Me aseguro que haya suficientes resultados
        self.query.add_pagination(start=0, limit=1000)
        data = self.query.run()['data']

        last_timestamp = data[-1][0]
        self.assertEqual(self.end_date, last_timestamp)

    def test_invalid_start_date(self):
        self.cmd.run(self.query, {'start_date': 'not a date'})
        self.assertTrue(self.cmd.errors)

    def test_invalid_end_date(self):
        self.cmd.run(self.query, {'end_date': 'not a date'})
        self.assertTrue(self.cmd.errors)

    def test_non_iso_end_date(self):
        self.cmd.run(self.query, {'end_date': '04-01-2010'})
        self.assertTrue(self.cmd.errors)

        self.cmd.run(self.query, {'end_date': '2010/04/01'})
        self.assertTrue(self.cmd.errors)

    def test_non_iso_start_date(self):
        self.cmd.run(self.query, {'start_date': '04-01-2010'})
        self.assertTrue(self.cmd.errors)

        self.cmd.run(self.query, {'start_date': '2010/04/01'})
        self.assertTrue(self.cmd.errors)

    def test_partial_end_date_is_inclusive(self):
        field = Field.objects.get(identifier=self.single_series)
        query = Query()
        query.add_series(self.field, 'value')
        query.sort('asc')
        first_date = query.run()['data'][0][0]

        end_date = iso8601.parse_date(first_date) + relativedelta(years=2)
        self.query.add_series(field, 'value')
        self.cmd.run(self.query, {'end_date': str(end_date)})

        # Me aseguro de traer suficientes resultados
        self.query.add_pagination(start=0, limit=1000)
        self.query.sort('asc')
        data = self.query.run()['data']

        last_date = iso8601.parse_date(data[-1][0])
        self.assertEqual(last_date.year, end_date.year)
        self.assertGreaterEqual(last_date.month, end_date.month)
