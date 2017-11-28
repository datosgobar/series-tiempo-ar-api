# coding=utf-8
import iso8601
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from nose.tools import raises

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.query import ESQuery
from .helpers import setup_database

SERIES_NAME = settings.TEST_SERIES_NAME.format('month')


class QueryTest(TestCase):

    start = constants.API_DEFAULT_VALUES['start']
    limit = constants.API_DEFAULT_VALUES['limit']

    default_limit = 10
    max_limit = 1000

    start_date = '2010-01-01'
    end_date = '2015-01-01'

    single_series = SERIES_NAME
    rep_mode = 'value'
    series_periodicity = 'month'  # Periodicidad de la serie anterior
    delayed_series = settings.TEST_SERIES_NAME_DELAYED.format('month')

    @classmethod
    def setUpClass(cls):
        setup_database()
        super(QueryTest, cls).setUpClass()

    def setUp(self):
        self.query = ESQuery(settings.TEST_INDEX)

    def test_initially_no_series(self):
        self.assertFalse(self.query.series)

    def test_pagination(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_pagination(self.start, self.limit)
        data = self.query.run()

        self.assertEqual(len(data), self.limit - self.start)

    def test_pagination_limit(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_pagination(self.start, self.max_limit)
        data = self.query.run()
        self.assertEqual(len(data), self.max_limit - self.start)

    def test_time_filter(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_filter(self.start_date, self.end_date)
        data = self.query.run()
        for row in data:
            if 'T' in row[0]:
                date = iso8601.parse_date(row[0])
                start_date = iso8601.parse_date(self.start_date)
                end_date = iso8601.parse_date(self.end_date)
            else:
                date = iso8601.parse_date(row[0])
                start_date = iso8601.parse_date(self.start_date)
                end_date = iso8601.parse_date(self.end_date)
            self.assertGreaterEqual(date, start_date)
            self.assertLessEqual(date, end_date)

    def test_execute_single_series(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        data = self.query.run()

        self.assertTrue(data)

    def test_default_return_limits(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        data = self.query.run()

        self.assertEqual(len(data), self.default_limit)

    def test_add_series(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        data = self.query.run()

        self.assertTrue(data)
        # Expected: rows de 2 datos: timestamp, valor de la serie
        self.assertTrue(len(data[0]) == 2)

    def test_add_two_series(self):
        self.query.add_series(self.single_series, 'value', periodicity=self.series_periodicity)
        self.query.add_series(self.single_series,
                              'percent_change',
                              periodicity=self.series_periodicity)
        data = self.query.run()

        self.assertTrue(data)
        # Expected: rows de 3 datos: timestamp, serie 1, serie 2
        self.assertTrue(len(data[0]) == 3)

    @raises(QueryError)
    def test_try_collapse(self):
        self.query.add_collapse(interval='year', agg='avg')

    def test_preserve_query_order(self):

        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_series(self.delayed_series,
                              self.rep_mode,
                              self.series_periodicity)

        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.sort('asc')
        first_date = query.run()[0][0]
        self.query.sort('asc')
        data = self.query.run()
        self.assertEqual(data[0][0], first_date)

    def test_query_fills_nulls(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_series(self.delayed_series,
                              self.rep_mode,
                              self.series_periodicity)

        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.sort('asc')
        delayed_first_date = iso8601.parse_date(query.run()[0][0])
        self.query.sort('asc')
        data = self.query.run()

        delayed_series_index = 1  # Primera serie agregada
        for row in data:
            current_date = iso8601.parse_date(row[0])
            if current_date < delayed_first_date:
                self.assertEqual(row[delayed_series_index], None)
            else:
                break

    def test_query_fills_nulls_second_series(self):
        self.query.add_series(self.delayed_series,
                              self.rep_mode,
                              self.series_periodicity)
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)

        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.sort('asc')
        delayed_first_date = iso8601.parse_date(query.run()[0][0])
        self.query.sort('asc')
        data = self.query.run()

        delayed_series_index = 2  # Segunda serie agregada
        for row in data:
            current_date = iso8601.parse_date(row[0])
            if current_date < delayed_first_date:
                self.assertEqual(row[delayed_series_index], None)
            else:
                break

    def test_index_continuity(self):
        self.query.add_series(self.delayed_series,
                              self.rep_mode,
                              self.series_periodicity)
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)

        self.query.sort('asc')

        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.sort('asc')
        first_date = query.run()[0][0]

        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.delayed_series, self.rep_mode, self.series_periodicity)
        query.sort('asc')
        last_date = query.run()[-1][0]

        self.query.sort('asc')
        data = self.query.run()
        self.assertEqual(data[0][0], first_date)
        self.assertEqual(data[-1][0], last_date)
        current_date = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            row_date = iso8601.parse_date(row[0])
            self.assertEqual(current_date + relativedelta(months=1), row_date)
            current_date = row_date

    def test_has_collapse(self):
        self.assertEqual(False, self.query.has_collapse())