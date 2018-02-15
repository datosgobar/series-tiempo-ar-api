#! coding: utf-8
from django.conf import settings
from django.test import TestCase

from series_tiempo_ar_api.apps.api.models import Field
from series_tiempo_ar_api.apps.api.query.pipeline import Pagination
from series_tiempo_ar_api.apps.api.query.query import Query
from ..helpers import get_series_id

SERIES_NAME = get_series_id('month')


class PaginationTests(TestCase):
    single_series = SERIES_NAME

    limit = 1000
    start = 50

    @classmethod
    def setUpClass(cls):
        cls.field = Field.objects.get(series_id=cls.single_series)
        super(cls, PaginationTests).setUpClass()

    def setUp(self):
        self.query = Query(index=settings.TEST_INDEX)
        self.cmd = Pagination()

    @classmethod
    def setUpClass(cls):
        cls.field = Field.objects.get(series_id=cls.single_series)
        super(cls, PaginationTests).setUpClass()

    def test_start(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.query.sort('asc')
        params = {'ids': self.single_series, 'limit': self.limit}

        # Query sin offset
        other_query = Query(index=settings.TEST_INDEX)
        other_query.add_series(self.single_series, self.field, 'value')
        other_query.sort('asc')
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
        self.query.sort(how='asc')
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
