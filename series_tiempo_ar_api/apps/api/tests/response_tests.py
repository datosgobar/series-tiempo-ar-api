#! coding: utf-8
from django.test import TestCase

from series_tiempo_ar_api.apps.api.models import Field
from series_tiempo_ar_api.apps.api.query.query import Query
from series_tiempo_ar_api.apps.api.response import ResponseFormatterGenerator


class ResponseTests(TestCase):
    single_series = 'random-0'

    @classmethod
    def setUpClass(cls):
        cls.query = Query()
        cls.query.add_series(cls.single_series,
                             Field.objects.get(series_id=cls.single_series))
        super(ResponseTests, cls).setUpClass()

    def test_csv_response(self):
        generator = ResponseFormatterGenerator('csv').get_formatter()
        response = generator.run(self.query, {})

        self.assertTrue(response.get('Content-Type'), 'text/csv')

    def test_json_response(self):
        generator = ResponseFormatterGenerator('json').get_formatter()
        response = generator.run(self.query, {})

        self.assertEqual(response.get('Content-Type'), 'application/json')
