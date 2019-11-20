# coding=utf-8
from copy import deepcopy

import iso8601
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.query import ESQuery
from series_tiempo_ar_api.apps.api.query.series_query import SeriesQuery
from .helpers import get_series_id

SERIES_NAME = get_series_id('month')


class QueryTest(TestCase):

    start = constants.API_DEFAULT_VALUES['start']
    limit = constants.API_DEFAULT_VALUES['limit']

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
        field = Field.objects.get(identifier=self.single_series)
        self.serie = SeriesQuery(field, self.rep_mode)
        delayed_serie_model = Field.objects.get(identifier=self.delayed_series)
        self.delayed_serie = SeriesQuery(delayed_serie_model, self.rep_mode)

    def _run_query(self, series=None):
        if series is None:
            series = [self.serie]
        return self.query.run_for_series(series)['data']

    def test_initially_no_series(self):
        self.assertFalse(self.query.series)

    def test_pagination(self):
        self.query.add_pagination(self.start, self.limit)
        data = self._run_query()

        self.assertEqual(len(data), self.limit - self.start)

    def test_pagination_limit(self):
        self.query.add_pagination(self.start, 15)
        self.query.sort(how='asc')
        data = self._run_query()
        self.assertEqual(len(data), 15)

    def test_execute_single_series(self):
        data = self._run_query()

        self.assertTrue(data)

    def test_default_return_limits(self):
        data = self._run_query()

        self.assertEqual(len(data), self.limit)

    def test_add_series(self):
        data = self._run_query()

        self.assertTrue(data)
        # Expected: rows de 2 datos: timestamp, valor de la serie
        self.assertTrue(len(data[0]) == 2)

    def test_add_two_series(self):
        data = self._run_query([self.serie, self.serie])

        self.assertTrue(data)
        # Expected: rows de 3 datos: timestamp, serie 1, serie 2
        self.assertTrue(len(data[0]) == 3)

    def test_preserve_query_order(self):
        data = self._run_query([self.serie, self.delayed_serie])

        query = ESQuery(index=settings.TS_INDEX)
        first_date = query.run_for_series([self.serie])['data'][0][0]
        self.assertEqual(data[0][0], first_date)

    def test_query_fills_nulls(self):
        data = self._run_query([self.serie, self.delayed_serie])
        first_date = iso8601.parse_date('2004-01-01')
        for row in data:
            current_date = iso8601.parse_date(row[0])
            if current_date < first_date:
                self.assertEqual(row[2], None)
            else:
                break

    def test_query_fills_nulls_second_series(self):
        data = self._run_query([self.delayed_serie, self.serie])
        first_date = iso8601.parse_date('2004-01-01')
        for row in data:
            current_date = iso8601.parse_date(row[0])
            if current_date < first_date:
                self.assertEqual(row[1], None)
            else:
                break

    def test_index_continuity(self):
        data = self._run_query([self.delayed_serie, self.serie])
        current_date = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            row_date = iso8601.parse_date(row[0])
            self.assertEqual(current_date + relativedelta(months=1), row_date)
            current_date = row_date

    def test_query_add_aggregation(self):
        data = self._run_query()

        self.serie._collapse_agg = 'sum'

        sum_data = self._run_query()

        for avg_row, sum_row in zip(data, sum_data):
            avg_value = avg_row[1]
            sum_value = sum_row[1]
            # En query común el parámetro collapse_agg NO TIENE EFECTO
            self.assertEqual(avg_value, sum_value)

    def test_sort(self):
        self.query.sort('desc')

        data = self._run_query()
        current_date = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            row_date = iso8601.parse_date(row[0])
            self.assertGreater(current_date, row_date)
            current_date = row_date

    def test_multiple_series_limit(self):
        limit = 100

        self.query.add_pagination(start=0, limit=limit)

        data = self._run_query([self.serie, self.delayed_serie])
        self.assertEqual(len(data), limit)

    def test_multiple_sort_desc_delayed(self):
        self.query.sort('desc')
        self.query.add_pagination(start=0, limit=1)
        row = self._run_query([self.serie, self.delayed_serie])[0]

        self.assertIsNotNone(row[2])
        self.assertIsNone(row[1])

    def test_same_series_rep_mode(self):
        serie_percent_change = deepcopy(self.serie)
        serie_percent_change.rep_mode = 'percent_change'

        data = self._run_query([self.serie, serie_percent_change])
        other_data = self._run_query([serie_percent_change, self.serie])

        # Esperado: mismos resultados, invertidos en orden de fila
        for row, other_row in zip(data, other_data):
            self.assertEqual(row[0], other_row[0])
            self.assertEqual(row[1], other_row[2])
            self.assertEqual(row[2], other_row[1])

    def test_max_without_collapse_same_as_avg(self):

        data = self._run_query()

        self.serie._collapse_agg = 'max'
        other_data = self._run_query()

        for row, max_row in zip(data, other_data):
            self.assertListEqual(row, max_row)

    def test_rep_mode_has_no_leading_nulls(self):
        self.serie.rep_mode = 'percent_change'
        data = self._run_query()

        self.assertIsNotNone(data[0][1])

    def test_year_rep_mode_has_no_leading_nulls(self):
        self.serie.rep_mode = 'percent_change_a_year_ago'
        data = self._run_query()

        self.assertIsNotNone(data[0][1])

    def test_query_count(self):
        self.query.add_series(self.single_series, self.rep_mode, self.series_periodicity)

        count = self.query.run_for_series([self.serie])['count']
        self.assertEqual(count, 12 * 10)
