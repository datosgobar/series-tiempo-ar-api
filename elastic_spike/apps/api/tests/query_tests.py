# coding=utf-8
import isodate
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.conf import settings
from elastic_spike.apps.api.query import Query, CollapseQuery


class QueryTest(TestCase):
    start = settings.API_DEFAULT_VALUES['start']
    limit = settings.API_DEFAULT_VALUES['limit']

    default_limit = 10
    max_limit = 1000

    start_date = '2010-01-01T03:00:00Z'
    end_date = '2015-01-01T03:00:00Z'

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
            date = isodate.parse_datetime(row[0])
            self.assertGreaterEqual(date,
                                    isodate.parse_datetime(self.start_date))
            self.assertLessEqual(date,
                                 isodate.parse_datetime(self.end_date))

    def test_execute_single_series(self):
        self.query.run()

        self.assertTrue(self.query.data)

    def test_default_return_limits(self):
        self.query.run()

        self.assertEqual(len(self.query.data), self.default_limit)

    def test_add_series(self):
        self.query.add_series('random-0', 'value')
        self.query.run()

        self.assertTrue(self.query.data)
        # Expected: rows de 2 datos: timestamp, valor de la serie
        self.assertTrue(len(self.query.data[0]) == 2)

    def test_add_two_series(self):
        self.query.add_series('random-0', 'value')
        self.query.add_series('random-0', 'percent_change')
        self.query.run()

        self.assertTrue(self.query.data)
        # Expected: rows de 3 datos: timestamp, serie 1, serie 2
        self.assertTrue(len(self.query.data[0]) == 3)


class CollapseQueryTests(TestCase):

    start = 10
    limit = 15

    def setUp(self):
        self.query = CollapseQuery()

    def test_execute_empty(self):
        self.query.run()

        self.assertFalse(self.query.data)

    def test_execute_single(self):
        self.query.add_series('random-0', 'value')

        self.query.run()
        self.assertTrue(self.query.data)

    def test_start_limit(self):
        self.query.add_series('random-0', 'value')
        self.query.add_pagination(self.start, self.limit)
        self.query.run()

        self.assertEqual(len(self.query.data), self.limit)

    def test_init_from_other(self):
        other_query = Query()
        other_query.add_series('random-0', 'value')
        self.query = CollapseQuery(other_query)
        self.query.run()

    def test_add_collapse(self):
        """Testea que luego de agregar un collapse default, los
        resultados sean anuales, es decir cada uno a un año de
        diferencia con su anterior"""
        self.query.add_series('random-0', 'value')
        self.query.add_collapse()
        self.query.run()
        prev_timestamp = None
        for row in self.query.data:
            timestamp = row[0]
            parsed_timestamp = isodate.parse_datetime(timestamp)
            if not prev_timestamp:
                prev_timestamp = parsed_timestamp
                continue
            delta = relativedelta(parsed_timestamp, prev_timestamp)
            self.assertTrue(delta.years == 1, timestamp)
            prev_timestamp = parsed_timestamp

    def test_collapse_custom_params(self):
        self.query.add_series('random-0', 'value')
        self.query.add_collapse(agg='sum', interval='quarter')
        self.query.run()
        prev_timestamp = None
        for row in self.query.data:
            timestamp = row[0]
            parsed_timestamp = isodate.parse_datetime(timestamp)
            if not prev_timestamp:
                prev_timestamp = parsed_timestamp
                continue
            delta = relativedelta(parsed_timestamp, prev_timestamp)
            self.assertTrue(delta.months == 3, timestamp)
            prev_timestamp = parsed_timestamp
