# coding=utf-8
import iso8601
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from nose.tools import raises

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.query import ESQuery
from series_tiempo_ar_api.apps.api.query.series_query import SeriesQuery
from .helpers import get_series_id

SERIES_NAME = get_series_id('month')


class QueryTest(TestCase):

    start = constants.API_DEFAULT_VALUES['start']
    limit = constants.API_DEFAULT_VALUES['limit']

    default_limit = constants.API_DEFAULT_VALUES['limit']
    max_limit = 1000

    start_date = '2010-01-01'
    end_date = '2015-01-01'

    single_series = SERIES_NAME
    rep_mode = 'value'
    series_periodicity = 'month'  # Periodicidad de la serie anterior
    delayed_series = settings.TEST_SERIES_NAME_DELAYED.format('month')

    @classmethod
    def setUpClass(cls):
        super(QueryTest, cls).setUpClass()

    def setUp(self):
        self.query = ESQuery(settings.TS_INDEX)

    def test_initially_no_series(self):
        self.assertFalse(self.query.series)

    def test_pagination(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_pagination(self.start, self.limit)
        data = self.query.run()['data']

        self.assertEqual(len(data), self.limit - self.start)

    def test_pagination_limit(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_pagination(self.start, 15)
        self.query.sort(how='asc')
        data = self.query.run()['data']
        self.assertEqual(len(data), 15)

    def test_execute_single_series(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        data = self.query.run()['data']

        self.assertTrue(data)

    def test_default_return_limits(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        data = self.query.run()['data']

        self.assertEqual(len(data), self.default_limit)

    def test_add_series(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        data = self.query.run()['data']

        self.assertTrue(data)
        # Expected: rows de 2 datos: timestamp, valor de la serie
        self.assertTrue(len(data[0]) == 2)

    def test_add_two_series(self):
        self.query.add_series(self.single_series, 'value', periodicity=self.series_periodicity)
        self.query.add_series(self.single_series,
                              'percent_change',
                              periodicity=self.series_periodicity)
        data = self.query.run()['data']

        self.assertTrue(data)
        # Expected: rows de 3 datos: timestamp, serie 1, serie 2
        self.assertTrue(len(data[0]) == 3)

    def test_preserve_query_order(self):

        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_series(self.delayed_series,
                              self.rep_mode,
                              self.series_periodicity)

        query = ESQuery(index=settings.TS_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.sort('asc')
        first_date = query.run()['data'][0][0]
        self.query.sort('asc')
        data = self.query.run()['data']
        self.assertEqual(data[0][0], first_date)

    def test_query_fills_nulls(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_series(self.delayed_series,
                              self.rep_mode,
                              self.series_periodicity)

        query = ESQuery(index=settings.TS_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.sort('asc')
        delayed_first_date = iso8601.parse_date(query.run()['data'][0][0])
        self.query.sort('asc')
        data = self.query.run()['data']

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

        query = ESQuery(index=settings.TS_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.sort('asc')
        delayed_first_date = iso8601.parse_date(query.run()['data'][0][0])
        self.query.sort('asc')
        data = self.query.run()['data']

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

        query = ESQuery(index=settings.TS_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.add_filter(start="2000")  # Garantiza datos vacíos entre 1999-2001
        query.add_pagination(start=0, limit=1000)
        query.sort('asc')

        data = self.query.run()['data']
        current_date = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            row_date = iso8601.parse_date(row[0])
            self.assertEqual(current_date + relativedelta(months=1), row_date)
            current_date = row_date

    def test_query_add_aggregation(self):
        avg_query = ESQuery(index=settings.TS_INDEX)
        avg_query.add_series(self.single_series, self.rep_mode, self.series_periodicity, 'avg')
        data = avg_query.run()['data']

        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity, 'sum')

        for i, row in enumerate(data):
            avg_value = data[i][1]
            sum_value = row[1]
            # En query común el parámetro collapse_agg NO TIENE EFECTO
            self.assertEqual(avg_value, sum_value)

    def test_semester_query(self):
        self.query.add_series(get_series_id('semester'), self.rep_mode, 'semester')
        data = self.query.run()['data']

        for row in data:
            date = iso8601.parse_date(row[0])
            self.assertTrue(date.month in (1, 7))

    def test_execute_single(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)

        data = self.query.run()['data']
        self.assertTrue(data)

    def test_start_limit(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_pagination(self.start, self.limit)
        data = self.query.run()['data']

        self.assertEqual(len(data), self.limit)

    def test_sort(self):
        self.query.add_series(self.delayed_series,
                              self.rep_mode,
                              self.series_periodicity)
        self.query.sort('desc')

        data = self.query.run()['data']
        current_date = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            row_date = iso8601.parse_date(row[0])
            self.assertGreater(current_date, row_date)
            current_date = row_date

    def test_multiple_series_limit(self):
        limit = 100
        self.query.add_series(get_series_id('day'),
                              self.rep_mode,
                              self.series_periodicity)
        self.query.add_series(settings.TEST_SERIES_NAME_DELAYED.format('day'),
                              self.rep_mode,
                              self.series_periodicity)
        self.query.add_pagination(start=0, limit=limit)
        self.query.sort('asc')

        data = self.query.run()['data']
        self.assertEqual(len(data), limit)

    def test_aggregation_on_yearly_series(self):
        """Esperado: Valores de la serie con y sin agregación son iguales, no
        hay valores que colapsar"""
        year_series = get_series_id('year')
        self.query.add_series(year_series, self.rep_mode, 'year')
        self.query.add_series(year_series, self.rep_mode, 'year', 'end_of_period')

        data = self.query.run()['data']

        for row in data:
            self.assertEqual(row[1], row[2])

    def test_multiple_sort_desc_delayed(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_series(self.delayed_series, self.rep_mode, self.series_periodicity)

        self.query.sort('desc')
        self.query.add_pagination(start=0, limit=1)
        row = self.query.run()['data'][0]

        self.assertIsNotNone(row[2])
        self.assertIsNone(row[1])

    def test_same_series_rep_mode(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_series(self.single_series, 'percent_change_a_year_ago', self.series_periodicity)

        data = self.query.run()['data']

        other_query = ESQuery(settings.TS_INDEX)
        other_query.add_series(self.single_series, 'percent_change_a_year_ago', self.series_periodicity)
        other_query.add_series(self.single_series, self.rep_mode, self.series_periodicity)

        other_data = other_query.run()['data']

        # Esperado: mismos resultados, invertidos en orden de fila
        for i, row in enumerate(data):
            other_row = other_data[i]
            self.assertEqual(row[0], other_row[0])
            self.assertEqual(row[1], other_row[2])
            self.assertEqual(row[2], other_row[1])

    def test_min_agg(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_pagination(start=0, limit=12)
        data = self.query.run()['data']

        other_query = ESQuery(settings.TS_INDEX)
        other_query.add_series(self.single_series, self.rep_mode, self.series_periodicity, collapse_agg='min')
        other_query.add_pagination(start=0, limit=1)
        other_query.add_collapse('year')

        other_data = other_query.run()['data']

        min_val = min([row[1] for row in data])

        self.assertAlmostEqual(min_val, other_data[0][1], places=5)

    def test_max_without_collapse_same_as_avg(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        data = self.query.run()['data']

        other_query = ESQuery(settings.TS_INDEX)
        other_query.add_series(self.single_series, self.rep_mode, self.series_periodicity, collapse_agg='max')
        other_data = other_query.run()['data']

        for i, row in enumerate(data):
            self.assertEqual(tuple(row), tuple(other_data[i]))

    def test_rep_mode_has_no_leading_nulls(self):
        self.query.add_series(self.single_series, 'percent_change', self.series_periodicity)
        data = self.query.run()['data']

        self.assertIsNotNone(data[0][1])

    def test_year_rep_mode_has_no_leading_nulls(self):
        self.query.add_series(self.single_series, 'percent_change_a_year_ago', self.series_periodicity)
        data = self.query.run()['data']

        self.assertIsNotNone(data[0][1])

    def test_query_count(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        count = self.query.run()['count']

        # Todas las series generadas tienen max_limit como longitud. Ver support/generate_data.py
        self.assertEqual(count, 12 * 10)
