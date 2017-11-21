# coding=utf-8
import iso8601
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from nose.tools import raises

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.query import ESQuery, CollapseQuery
from .helpers import setup_database


class QueryTest(TestCase):

    start = constants.API_DEFAULT_VALUES['start']
    limit = constants.API_DEFAULT_VALUES['limit']

    default_limit = 10
    max_limit = 1000

    start_date = '2010-01-01'
    end_date = '2015-01-01'

    single_series = 'random_series-month-0'

    @classmethod
    def setUpClass(cls):
        setup_database()
        super(QueryTest, cls).setUpClass()

    def setUp(self):
        self.query = ESQuery(settings.TEST_INDEX)

    def test_initially_no_series(self):
        self.assertFalse(self.query.series)

    def test_pagination(self):
        self.query.add_series(self.single_series)
        self.query.add_pagination(self.start, self.limit)
        data = self.query.run()

        self.assertEqual(len(data), self.limit - self.start)

    def test_pagination_limit(self):
        self.query.add_series(self.single_series)
        self.query.add_pagination(self.start, self.max_limit)
        data = self.query.run()
        self.assertEqual(len(data), self.max_limit - self.start)

    def test_time_filter(self):
        self.query.add_series(self.single_series)
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
        self.query.add_series(self.single_series)
        data = self.query.run()

        self.assertTrue(data)

    def test_default_return_limits(self):
        self.query.add_series(self.single_series)
        data = self.query.run()

        self.assertEqual(len(data), self.default_limit)

    def test_add_series(self):
        self.query.add_series(self.single_series)
        data = self.query.run()

        self.assertTrue(data)
        # Expected: rows de 2 datos: timestamp, valor de la serie
        self.assertTrue(len(data[0]) == 2)

    def test_add_two_series(self):
        self.query.add_series(self.single_series, 'value')
        self.query.add_series(self.single_series, 'percent_change')
        data = self.query.run()

        self.assertTrue(data)
        # Expected: rows de 3 datos: timestamp, serie 1, serie 2
        self.assertTrue(len(data[0]) == 3)


class CollapseQueryTests(TestCase):

    start = 10
    limit = 15

    single_series = 'random_series-month-0'

    @classmethod
    def setUpClass(cls):
        setup_database()
        super(CollapseQueryTests, cls).setUpClass()

    def setUp(self):
        self.query = CollapseQuery(index=settings.TEST_INDEX)

    @raises(QueryError)
    def test_execute_empty(self):
        data = self.query.run()

        self.assertFalse(data)

    def test_execute_single(self):
        self.query.add_series(self.single_series)

        data = self.query.run()
        self.assertTrue(data)

    def test_start_limit(self):
        self.query.add_series(self.single_series)
        self.query.add_pagination(self.start, self.limit)
        data = self.query.run()

        self.assertEqual(len(data), self.limit)

    def test_init_from_other(self):
        other_query = ESQuery(index=settings.TEST_INDEX)
        other_query.add_series(self.single_series)
        self.query = CollapseQuery(settings.TEST_INDEX, other=other_query)
        self.query.add_collapse()
        data = self.query.run()
        self.assertTrue(data)

    def test_add_collapse(self):
        """Testea que luego de agregar un collapse default, los
        resultados sean anuales, es decir cada uno a un año de
        diferencia con su anterior"""
        self.query.add_series(self.single_series)
        self.query.add_collapse()
        data = self.query.run()
        prev_timestamp = None
        for row in data:
            timestamp = row[0]
            parsed_timestamp = iso8601.parse_date(timestamp)
            if not prev_timestamp:
                prev_timestamp = parsed_timestamp
                continue
            delta = relativedelta(parsed_timestamp, prev_timestamp)
            self.assertTrue(delta.years == 1, timestamp)
            prev_timestamp = parsed_timestamp

    def test_collapse_custom_params(self):
        self.query.add_series(self.single_series)
        self.query.add_collapse(interval='quarter')
        data = self.query.run()
        prev_timestamp = None
        for row in data:
            timestamp = row[0]
            parsed_timestamp = iso8601.parse_date(timestamp)
            if not prev_timestamp:
                prev_timestamp = parsed_timestamp
                continue
            delta = relativedelta(parsed_timestamp, prev_timestamp)
            self.assertTrue(delta.months == 3, timestamp)
            prev_timestamp = parsed_timestamp

    def test_add_two_collapses(self):
        """Esperado: El segundo collapse overridea el primero"""
        self.query.add_series(self.single_series)
        self.query.add_collapse(interval='quarter')
        self.query.add_collapse(interval='year')
        data = self.query.run()

        prev_timestamp = None
        for row in data:
            timestamp = row[0]
            parsed_timestamp = iso8601.parse_date(timestamp)
            if not prev_timestamp:
                prev_timestamp = parsed_timestamp
                continue
            delta = relativedelta(parsed_timestamp, prev_timestamp)
            self.assertTrue(delta.years == 1, timestamp)
            prev_timestamp = parsed_timestamp

    def test_init_from_other_collapse_query(self):
        other_query = CollapseQuery(index=settings.TEST_INDEX)
        other_query.add_series(self.single_series)
        self.query = CollapseQuery(index=settings.TEST_INDEX, other=other_query)
        data = self.query.run()
        self.assertTrue(data)
