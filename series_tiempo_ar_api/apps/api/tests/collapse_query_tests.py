#! coding: utf-8
import iso8601
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from nose.tools import raises

from series_tiempo_ar_api.apps.api.exceptions import QueryError, EndOfPeriodError
from series_tiempo_ar_api.apps.api.query.es_query.collapse_query import CollapseQuery
from series_tiempo_ar_api.apps.api.query.es_query.es_query import ESQuery

SERIES_NAME = settings.TEST_SERIES_NAME.format('month')


class CollapseQueryTests(TestCase):

    start = 10
    limit = 15

    single_series = SERIES_NAME
    rep_mode = 'value'
    series_periodicity = 'month'

    # Serie cuya primera fecha está mucho más tarde que la anterior
    delayed_series = settings.TEST_SERIES_NAME_DELAYED.format('month')

    @classmethod
    def setUpClass(cls):
        super(CollapseQueryTests, cls).setUpClass()

    def setUp(self):
        self.query = CollapseQuery(index=settings.TEST_INDEX)

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

    def test_init_from_other(self):
        other_query = ESQuery(index=settings.TEST_INDEX)
        other_query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query = CollapseQuery(settings.TEST_INDEX, other=other_query)
        self.query.add_collapse()
        data = self.query.run()
        self.assertTrue(data)

    def test_add_collapse(self):
        """Testea que luego de agregar un collapse default, los
        resultados sean anuales, es decir cada uno a un año de
        diferencia con su anterior"""
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
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
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
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
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
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
        other_query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query = CollapseQuery(index=settings.TEST_INDEX, other=other_query)
        data = self.query.run()
        self.assertTrue(data)

    def test_preserve_query_order(self):

        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        self.query.add_series(self.delayed_series,
                              self.rep_mode,
                              self.series_periodicity)

        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.sort('asc')
        first_date = query.run()[0][0]
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
        self.query.add_pagination(0, 1000)

        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity)
        query.sort('asc')
        first_date = query.run()[0][0]

        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.delayed_series, self.rep_mode, self.series_periodicity)
        query.sort('desc')
        last_date = query.run()[0][0]

        data = self.query.run()
        self.assertEqual(iso8601.parse_date(data[0][0]).year,
                         iso8601.parse_date(first_date).year)
        self.assertEqual(iso8601.parse_date(data[-1][0]).year,
                         iso8601.parse_date(last_date).year)
        current_date = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            row_date = iso8601.parse_date(row[0])
            self.assertEqual(current_date + relativedelta(years=1), row_date)
            current_date = row_date

    def test_has_collapse(self):
        self.assertEqual(True, self.query.has_collapse())

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
        avg_query = CollapseQuery(index=settings.TEST_INDEX)
        avg_query.add_series(self.single_series, self.rep_mode, self.series_periodicity, 'avg')
        data = avg_query.run()

        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity, 'sum')
        sum_data = self.query.run()

        for i, row in enumerate(sum_data):
            # Suma debe ser siempre mayor que el promedio
            sum_value = row[1]
            avg_value = data[i][1]
            self.assertGreater(sum_value, avg_value)

    def test_take_agg_from_other_query(self):
        query = ESQuery(index=settings.TEST_INDEX)
        query.add_series(self.single_series, self.rep_mode, self.series_periodicity, 'sum')

        self.query = CollapseQuery(index=settings.TEST_INDEX, other=query)

        sum_query = CollapseQuery(index=settings.TEST_INDEX)
        sum_query.add_series(self.single_series, self.rep_mode, self.series_periodicity, 'sum')

        data = self.query.run()
        expected_data = sum_query.run()

        self.assertListEqual(data, expected_data)

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

    @raises(EndOfPeriodError)
    def test_end_of_period_before_1970(self):
        """Si la serie tiene fechas menores a 1970, se lanza una excepción
        La implementación actual de end of period depende de UNIX timestamps, cuyo
        mínimo valor es 1970-01-01
        """
        self.query.add_series(self.single_series,
                              self.rep_mode,
                              self.series_periodicity,
                              'end_of_period')
        self.query.add_collapse('year')
        self.query.run()

    def test_end_of_period_with_rep_mode(self):
        self.query.add_series(self.single_series,
                              'percent_change',
                              self.series_periodicity,
                              'end_of_period')
        self.query.add_collapse('year')
        self.query.add_filter(start="1970")
        data = self.query.run()

        orig_eop = CollapseQuery(index=settings.TEST_INDEX)
        orig_eop.add_series(self.single_series,
                            self.rep_mode,
                            self.series_periodicity,
                            'end_of_period')
        orig_eop.add_filter(start="1970")
        orig_eop.add_collapse('year')
        end_of_period = orig_eop.run()

        for i, row in enumerate(data[1:], 1):  # El primero es nulo en pct change
            value = end_of_period[i][1] / end_of_period[i - 1][1] - 1

            self.assertAlmostEqual(value, row[1])
