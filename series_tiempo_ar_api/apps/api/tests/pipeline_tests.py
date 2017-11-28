#! coding: utf-8
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from iso8601 import iso8601

from series_tiempo_ar_api.apps.api.models import Field
from series_tiempo_ar_api.apps.api.query.pipeline import \
    NameAndRepMode, Collapse, Pagination, DateFilter, Sort, CollapseAggregation
from series_tiempo_ar_api.apps.api.query.query import Query
from series_tiempo_ar_api.apps.api.query.strings import SERIES_DOES_NOT_EXIST
from .helpers import setup_database
from .support.pipeline import time_serie_name

SERIES_NAME = settings.TEST_SERIES_NAME.format('month')


class NameAndRepModeTest(TestCase):
    """Testea el comando que se encarga del parámetro 'ids' de la
    query: el parseo de IDs de series y modos de representación de las
    mismas.
    """
    single_series = SERIES_NAME
    single_series_rep_mode = SERIES_NAME + ':percent_change'

    multi_series = SERIES_NAME + ',' + SERIES_NAME

    @classmethod
    def setUpClass(cls):
        setup_database()
        super(cls, NameAndRepModeTest).setUpClass()

    def setUp(self):
        self.cmd = NameAndRepMode()
        self.query = Query(index=settings.TEST_INDEX)

    def test_invalid_series(self):
        invalid_series = 'invalid'
        self.cmd.run(self.query, {'ids': invalid_series})
        self.assertTrue(self.cmd.errors)

    def test_serie_does_not_exist_message(self):
        invalid_series = time_serie_name()
        self.cmd.run(self.query, {'ids': invalid_series})
        base_msg = SERIES_DOES_NOT_EXIST.format('')
        self.assertIn(base_msg, self.cmd.errors[0]["error"])

    def test_valid_series(self):
        self.cmd.run(self.query, {'ids': self.single_series})
        self.assertFalse(self.cmd.errors)

    def test_global_rep_mode(self):
        self.cmd.run(self.query, {'ids': self.single_series})
        self.query.sort('asc')
        data = self.query.run()['data']

        other_query = Query(index=settings.TEST_INDEX)
        self.cmd.run(other_query, {'ids': self.single_series,
                                   'representation_mode': 'change'})
        other_query.sort('asc')
        other_data = other_query.run()['data']

        for index, row in enumerate(other_data[1:], start=1):
            change = data[index][1] - data[index - 1][1]
            self.assertEqual(row[1], change)

    def test_multiple_series(self):
        self.cmd.run(self.query, {'ids': self.multi_series})
        data = self.query.run()['data']

        self.assertTrue(len(data[0]), 3)

    def test_leading_comma(self):
        self.cmd.run(self.query, {'ids': ',' + SERIES_NAME})
        self.assertTrue(self.cmd.errors)

    def test_final_comma(self):
        self.cmd.run(self.query, {'ids': SERIES_NAME + ','})
        self.assertTrue(self.cmd.errors)

    def test_one_valid_one_invalid(self):
        self.cmd.run(self.query, {'ids': SERIES_NAME + ',invalid'})
        self.assertTrue(self.cmd.errors)

    def test_second_valid_first_invalid(self):
        self.cmd.run(self.query, {'ids': 'invalid,' + SERIES_NAME})
        self.assertTrue(self.cmd.errors)

    def test_invalid_rep_mode(self):
        self.cmd.run(self.query, {'ids': SERIES_NAME + ':' + SERIES_NAME})
        self.assertTrue(self.cmd.errors)

    def test_leading_semicolon(self):
        self.cmd.run(self.query, {'ids': ':' + SERIES_NAME})
        self.assertTrue(self.cmd.errors)

    def test_final_semicolon(self):
        self.cmd.run(self.query, {'ids': SERIES_NAME + ':'})
        self.assertTrue(self.cmd.errors)


class CollapseTest(TestCase):
    single_series = SERIES_NAME

    @classmethod
    def setUpClass(cls):
        setup_database()
        super(cls, CollapseTest).setUpClass()

    def setUp(self):
        self.query = Query(index=settings.TEST_INDEX)
        self.cmd = Collapse()

    def test_valid_aggregation(self):
        self.cmd.run(self.query, {'ids': self.single_series,
                                  'collapse:': 'year',
                                  'collapse_aggregation': 'sum'})
        self.assertFalse(self.cmd.errors)


class CollapseAggregationTests(TestCase):

    def setUp(self):
        self.query = Query()
        self.cmd = CollapseAggregation()

    def test_invalid_aggregation(self):
        self.cmd.run(self.query, {'collapse_aggregation': 'INVALID'})
        self.assertTrue(self.cmd.errors)


class PaginationTests(TestCase):
    single_series = SERIES_NAME

    limit = 1000
    start = 50

    @classmethod
    def setUpClass(cls):
        setup_database()
        cls.field = Field.objects.get(series_id=cls.single_series)
        super(cls, PaginationTests).setUpClass()

    def setUp(self):
        self.query = Query(index=settings.TEST_INDEX)
        self.cmd = Pagination()

    @classmethod
    def setUpClass(cls):
        setup_database()
        cls.field = Field.objects.get(series_id=cls.single_series)
        super(cls, PaginationTests).setUpClass()

    def test_start(self):
        self.query.add_series(self.single_series, self.field, 'value')
        params = {'ids': self.single_series, 'limit': self.limit}

        # Query sin offset
        other_query = Query(index=settings.TEST_INDEX)
        other_query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(other_query, params)
        other_data = other_query.run()['data']

        # Query con un offset de 'start'
        params_start = params.copy()
        params_start['start'] = self.start
        self.cmd.run(self.query, params_start)
        data = self.query.run()['data']

        # Los datos del primer query empiezan en un offset de start en el otro
        self.assertEqual(data[0], other_data[self.start])

    def test_limit(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'ids': self.single_series,
                                  'limit': self.limit})
        data = self.query.run()['data']
        self.assertEqual(len(data), self.limit)

    def test_invalid_start_parameter(self):
        self.query.add_series(self.single_series, self.field, 'value')

        self.cmd.run(self.query, {'ids': self.single_series,
                                  'start': 'not a number'})
        self.query.run()
        self.assertTrue(self.cmd.errors)

    def test_invalid_limit_parameter(self):
        self.cmd.run(self.query, {'ids': self.single_series,
                                  'limit': 'not a number'})
        self.assertTrue(self.cmd.errors)

    def test_start_over_limit(self):
        self.cmd.run(self.query, {'ids': self.single_series,
                                  'start': '99999999'})
        self.assertTrue(self.cmd.errors)

    def start_limit_over_limit(self):
        self.cmd.run(self.query, {'ids': self.single_series,
                                  'limit': '99999999'})
        self.assertTrue(self.cmd.errors)


class DateFilterTests(TestCase):
    single_series = SERIES_NAME

    start_date = '1980-01-01'
    end_date = '1985-01-01'

    @classmethod
    def setUpClass(cls):
        setup_database()
        cls.field = Field.objects.get(series_id=cls.single_series)
        super(cls, DateFilterTests).setUpClass()

    def setUp(self):
        self.query = Query(index=settings.TEST_INDEX)
        self.cmd = DateFilter()

    @classmethod
    def setUpClass(cls):
        setup_database()
        cls.field = Field.objects.get(series_id=cls.single_series)
        super(cls, DateFilterTests).setUpClass()

    def test_start_date(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'start_date': self.start_date})
        self.query.sort('asc')

        data = self.query.run()['data']

        first_timestamp = data[0][0]
        self.assertEqual(self.start_date, first_timestamp)

    def test_end_date(self):
        self.query.add_series(self.single_series, self.field, 'value')
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
        query = Query(index=settings.TEST_INDEX)
        query.add_series(self.single_series, self.field, 'value')
        first_date = query.run()['data'][0][0]

        end_date = iso8601.parse_date(first_date) + relativedelta(years=10)
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'end_date': str(end_date)})

        # Me aseguro de traer suficientes resultados
        self.query.add_pagination(start=0, limit=1000)
        self.query.sort('asc')
        data = self.query.run()['data']
        # Trajo resultados hasta 2005 inclusive
        last_date = iso8601.parse_date(data[-1][0])
        self.assertEqual(last_date.year, end_date.year)
        self.assertGreaterEqual(last_date.month, end_date.month)


class SortTests(TestCase):

    single_series = SERIES_NAME

    @classmethod
    def setUpClass(cls):
        cls.field = Field.objects.get(series_id=SERIES_NAME)
        super(cls, SortTests).setUpClass()

    def setUp(self):
        self.query = Query(index=settings.TEST_INDEX)
        self.cmd = Sort()

    def test_add_asc_sort(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'sort': 'asc'})

        data = self.query.run()['data']

        previous = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            current = iso8601.parse_date(row[0])
            self.assertGreater(current, previous)
            previous = current

    def test_add_desc_sort(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'sort': 'desc'})

        data = self.query.run()['data']

        previous = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            current = iso8601.parse_date(row[0])
            self.assertLess(current, previous)
            previous = current

    def test_sort_desc_with_collapse(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'sort': 'desc'})
        self.query.add_collapse(collapse='year')
        data = self.query.run()['data']

        previous = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            current = iso8601.parse_date(row[0])
            self.assertLess(current, previous)
            previous = current

    def test_sort_asc_with_collapse(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'sort': 'asc'})
        self.query.add_collapse(collapse='year')
        data = self.query.run()['data']

        previous = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            current = iso8601.parse_date(row[0])
            self.assertGreater(current, previous)
            previous = current

    def test_invalid_sort(self):
        self.cmd.run(self.query, {'sort': 'invalid'})
        self.assertTrue(self.cmd.errors)
