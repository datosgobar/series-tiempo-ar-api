# coding=utf-8
import iso8601
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from nose.tools import raises

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.query import ESQuery
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
        self.query.sort(how='asc')
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
        self.query.add_filter(start="1910", end="1920")
        self.query.sort('asc')

        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.add_filter(start="1921")  # Garantiza datos vacíos entre 1920-1921
        query.add_pagination(start=0, limit=1000)
        query.sort('asc')

        data = self.query.run()
        current_date = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            row_date = iso8601.parse_date(row[0])
            self.assertEqual(current_date + relativedelta(months=1), row_date)
            current_date = row_date

    def test_query_add_aggregation(self):
        avg_query = ESQuery(index=settings.TEST_INDEX)
        avg_query.add_series(self.single_series, self.rep_mode, self.series_periodicity, 'avg')
        data = avg_query.run()

        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity, 'sum')

        for i, row in enumerate(data):
            avg_value = data[i][1]
            sum_value = row[1]
            # En query común el parámetro collapse_agg NO TIENE EFECTO
            self.assertEqual(avg_value, sum_value)

    def test_semester_query(self):
        self.query.add_series(get_series_id('semester'), self.rep_mode, 'semester')
        data = self.query.run()

        for row in data:
            date = iso8601.parse_date(row[0])
            self.assertTrue(date.month in (1, 7))

    @raises(QueryError)
    def test_execute_empty(self):
        data = self.query.run()

        self.assertFalse(data)

    def test_execute_single(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)

        data = self.query.run()
        self.assertTrue(data)

    def test_start_limit(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_pagination(self.start, self.limit)
        data = self.query.run()

        self.assertEqual(len(data), self.limit)

    def test_add_collapse(self):
        """Testea que luego de agregar un collapse default, los
        resultados sean anuales, es decir cada uno a un año de
        diferencia con su anterior"""
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_collapse(interval='year')
        self.query.sort(how='asc')
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
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_collapse(interval='quarter')
        self.query.sort(how='asc')
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
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_collapse(interval='quarter')
        self.query.add_collapse(interval='year')
        self.query.sort(how='asc')
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

    def test_sort(self):
        self.query.add_series(self.delayed_series,
                              self.rep_mode,
                              self.series_periodicity)
        self.query.sort('desc')

        data = self.query.run()
        current_date = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            row_date = iso8601.parse_date(row[0])
            self.assertGreater(current_date, row_date)
            current_date = row_date

    def test_add_query_aggregation(self):
        avg_query = ESQuery(index=settings.TEST_INDEX)
        avg_query.add_series(self.single_series, self.rep_mode, self.series_periodicity, 'avg')
        data = avg_query.run()

        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity, 'sum')
        sum_data = self.query.run()

        for i, row in enumerate(sum_data):
            # Suma debe ser siempre mayor que el promedio
            sum_value = row[1]
            avg_value = data[i][1]
            self.assertGreater(sum_value, avg_value)

    def test_end_of_period(self):
        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.add_pagination(start=0, limit=1000)
        query.sort('asc')
        query.add_filter(start="1970")
        orig_data = query.run()

        self.query.add_series(self.single_series,
                              self.rep_mode,
                              self.series_periodicity,
                              'end_of_period')
        self.query.add_filter(start="1970")
        self.query.add_collapse('year')
        eop_data = self.query.run()

        for eop_row in eop_data:
            eop_value = eop_row[1]
            year = iso8601.parse_date(eop_row[0]).year
            for row in orig_data:
                row_date = iso8601.parse_date(row[0])
                if row_date.year == year and row_date.month == 12:
                    self.assertAlmostEqual(eop_value, row[1], 5)  # EOP trae pérdida de precisión
                    break

    def test_end_of_period_with_rep_mode(self):
        self.query.add_series(self.single_series,
                              'percent_change',
                              self.series_periodicity,
                              'end_of_period')
        self.query.add_collapse('year')
        self.query.sort('asc')
        data = self.query.run()

        orig_eop = ESQuery(index=settings.TEST_INDEX)
        orig_eop.add_series(self.single_series,
                            self.rep_mode,
                            self.series_periodicity,
                            'end_of_period')
        orig_eop.add_collapse('year')
        orig_eop.sort('asc')
        end_of_period = orig_eop.run()

        for i, row in enumerate(data):  # El primero es nulo en pct change
            value = end_of_period[i + 1][1] / end_of_period[i][1] - 1

            self.assertAlmostEqual(value, row[1])

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

        data = self.query.run()
        self.assertEqual(len(data), limit)

    def test_aggregation_on_yearly_series(self):
        """Esperado: Valores de la serie con y sin agregación son iguales, no
        hay valores que colapsar"""
        year_series = get_series_id('year')
        self.query.add_series(year_series, self.rep_mode, 'year')
        self.query.add_series(year_series, self.rep_mode, 'year', 'end_of_period')

        data = self.query.run()

        for row in data:
            self.assertEqual(row[1], row[2])

    def test_multiple_sort_desc_delayed(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_series(self.delayed_series, self.rep_mode, self.series_periodicity)

        self.query.sort('desc')

        data = self.query.run()

        for row in data:
            self.assertIsNotNone(row[2])
            self.assertIsNone(row[1])

    def test_same_series_rep_mode(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_series(self.single_series, 'percent_change_a_year_ago', self.series_periodicity)

        data = self.query.run()

        other_query = ESQuery(settings.TEST_INDEX)
        other_query.add_series(self.single_series, 'percent_change_a_year_ago', self.series_periodicity)
        other_query.add_series(self.single_series, self.rep_mode, self.series_periodicity)

        other_data = other_query.run()

        # Esperado: mismos resultados, invertidos en orden de fila
        for i, row in enumerate(data):
            other_row = other_data[i]
            self.assertEqual(row[0], other_row[0])
            self.assertEqual(row[1], other_row[2])
            self.assertEqual(row[2], other_row[1])

    def test_min_agg(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_pagination(start=0, limit=12)
        data = self.query.run()

        other_query = ESQuery(settings.TEST_INDEX)
        other_query.add_series(self.single_series, self.rep_mode, self.series_periodicity, collapse_agg='min')
        other_query.add_pagination(start=0, limit=1)
        other_query.add_collapse('year')

        other_data = other_query.run()

        min_val = min([row[1] for row in data])

        self.assertAlmostEqual(min_val, other_data[0][1], places=5)

    def test_max_agg(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_pagination(start=0, limit=12)
        data = self.query.run()

        other_query = ESQuery(settings.TEST_INDEX)
        other_query.add_series(self.single_series, self.rep_mode, self.series_periodicity, collapse_agg='max')
        other_query.add_pagination(start=0, limit=1)
        other_query.add_collapse('year')

        other_data = other_query.run()

        min_val = max([row[1] for row in data])

        self.assertAlmostEqual(min_val, other_data[0][1], places=5)

    def test_max_without_collapse_same_as_avg(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        data = self.query.run()

        other_query = ESQuery(settings.TEST_INDEX)
        other_query.add_series(self.single_series, self.rep_mode, self.series_periodicity, collapse_agg='max')
        other_data = other_query.run()

        for i, row in enumerate(data):
            self.assertEqual(tuple(row), tuple(other_data[i]))

    def test_min_max_collapse_agg_with_rep_mode(self):
        self.query.add_series(self.single_series, 'percent_change', self.series_periodicity)
        self.query.add_pagination(start=1, limit=12)
        data = self.query.run()

        other_query = ESQuery(settings.TEST_INDEX)
        other_query.add_series(self.single_series, 'percent_change', self.series_periodicity, collapse_agg='max')
        other_query.add_pagination(start=0, limit=1)
        other_query.add_collapse('year')

        other_data = other_query.run()

        min_val = max([row[1] for row in data])

        self.assertAlmostEqual(min_val, other_data[0][1], places=5)

    def test_rep_mode_has_no_leading_nulls(self):
        self.query.add_series(self.single_series, 'percent_change', self.series_periodicity)
        data = self.query.run()

        self.assertIsNotNone(data[0][1])

    def test_year_rep_mode_has_no_leading_nulls(self):
        self.query.add_series(self.single_series, 'percent_change_a_year_ago', self.series_periodicity)
        data = self.query.run()

        self.assertIsNotNone(data[0][1])
