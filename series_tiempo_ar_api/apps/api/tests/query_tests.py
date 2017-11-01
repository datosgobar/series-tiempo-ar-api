# coding=utf-8
import iso8601
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from nose.tools import raises

from series_tiempo_ar_api.apps.api.query.query import Query, CollapseQuery, \
    CollapseError
from .helpers import setup_database


class QueryTest(TestCase):

    start = settings.API_DEFAULT_VALUES['start']
    limit = settings.API_DEFAULT_VALUES['limit']

    default_limit = 10
    max_limit = 1000

    start_date = '2010-01-01'
    end_date = '2015-01-01'

    single_series = 'random-0'

    @classmethod
    def setUpClass(cls):
        setup_database()
        super(QueryTest, cls).setUpClass()

    def setUp(self):
        self.query = Query()

    def test_inicialmente_no_hay_series(self):
        self.assertFalse(self.query.series)

    def test_pagination_agrega_serie_si_no_existe(self):
        self.query.add_pagination(self.start, self.limit)

        self.assertEqual(len(self.query.series), 1)

    def test_pagination_no_agrega_serie_si_ya_existe_una(self):
        self.query.add_pagination(self.start, self.limit)
        self.query.add_pagination(self.start, self.limit)

        self.assertEqual(len(self.query.series), 1)

    def test_pagination(self):
        self.query.add_pagination(self.start, self.limit)
        self.query.run()

        self.assertEqual(len(self.query.data), self.limit - self.start)

    def test_pagination_limit(self):
        self.query.add_pagination(self.start, self.max_limit)
        self.query.run()
        self.assertEqual(len(self.query.data), self.max_limit - self.start)

    def test_time_filter(self):
        self.query.add_filter(self.start_date, self.end_date)
        self.query.run()
        for row in self.query.data:
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
        self.query.run()

        self.assertTrue(self.query.data)

    def test_default_return_limits(self):
        self.query.run()

        self.assertEqual(len(self.query.data), self.default_limit)

    def test_add_series(self):
        self.query.add_series(self.single_series)
        self.query.run()

        self.assertTrue(self.query.data)
        # Expected: rows de 2 datos: timestamp, valor de la serie
        self.assertTrue(len(self.query.data[0]) == 2)

    def test_add_two_series(self):
        self.query.add_series(self.single_series, 'value')
        self.query.add_series(self.single_series, 'percent_change')
        self.query.run()

        self.assertTrue(self.query.data)
        # Expected: rows de 3 datos: timestamp, serie 1, serie 2
        self.assertTrue(len(self.query.data[0]) == 3)

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


class CollapseQueryTests(TestCase):

    start = 10
    limit = 15

    single_series = 'random-0'

    @classmethod
    def setUpClass(cls):
        setup_database()
        super(CollapseQueryTests, cls).setUpClass()

    def setUp(self):
        self.query = CollapseQuery()

    def test_execute_empty(self):
        self.query.run()

        self.assertFalse(self.query.data)

    def test_execute_single(self):
        self.query.add_series(self.single_series)

        self.query.run()
        self.assertTrue(self.query.data)

    def test_start_limit(self):
        self.query.add_series(self.single_series)
        self.query.add_pagination(self.start, self.limit)
        self.query.run()

        self.assertEqual(len(self.query.data), self.limit)

    def test_init_from_other(self):
        other_query = Query()
        other_query.add_series(self.single_series)
        self.query = CollapseQuery(other_query)
        self.query.run()

    def test_add_collapse(self):
        """Testea que luego de agregar un collapse default, los
        resultados sean anuales, es decir cada uno a un año de
        diferencia con su anterior"""
        self.query.add_series(self.single_series)
        self.query.add_collapse()
        self.query.run()
        prev_timestamp = None
        for row in self.query.data:
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
        self.query.run()
        prev_timestamp = None
        for row in self.query.data:
            timestamp = row[0]
            parsed_timestamp = iso8601.parse_date(timestamp)
            if not prev_timestamp:
                prev_timestamp = parsed_timestamp
                continue
            delta = relativedelta(parsed_timestamp, prev_timestamp)
            self.assertTrue(delta.months == 3, timestamp)
            prev_timestamp = parsed_timestamp

    def test_index_metadata_frequency(self):
        collapse_interval = 'quarter'
        self.query.add_series(self.single_series)
        self.query.add_collapse(interval=collapse_interval)
        self.query.run()

        index_frequency = self.query.get_metadata()[0]['frequency']
        self.assertEqual(index_frequency, collapse_interval)

    def test_index_metadata_start_end_dates(self):
        collapse_interval = 'quarter'
        self.query.add_series(self.single_series)
        self.query.add_collapse(interval=collapse_interval)
        self.query.run()

        index_meta = self.query.get_metadata()[0]
        self.assertEqual(self.query.data[0][0], index_meta['start_date'])
        self.assertEqual(self.query.data[-1][0], index_meta['end_date'])

    @raises(CollapseError)
    def test_invalid_collapse(self):
        collapse_interval = 'day'  # Serie cargada es mensual
        self.query.add_series(self.single_series)
        self.query.add_collapse(interval=collapse_interval)
