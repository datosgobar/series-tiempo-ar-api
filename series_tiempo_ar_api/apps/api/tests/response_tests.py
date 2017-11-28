#! coding: utf-8
from django.conf import settings
from django.test import TestCase

from series_tiempo_ar_api.apps.api.models import Field
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.query import Query
from series_tiempo_ar_api.apps.api.query.response import \
    ResponseFormatterGenerator
from series_tiempo_ar_api.apps.api.tests.helpers import setup_database


class ResponseTests(TestCase):
    single_series = settings.TEST_SERIES_NAME.format('month')

    @classmethod
    def setUpClass(cls):
        setup_database()
        cls.query = Query(index=settings.TEST_INDEX)
        field = Field.objects.get(series_id=cls.single_series)
        cls.query.add_series(cls.single_series, field)
        cls.series_name = field.title
        super(ResponseTests, cls).setUpClass()

    def test_csv_response(self):
        generator = ResponseFormatterGenerator('csv').get_formatter()
        response = generator.run(self.query, {})

        self.assertTrue(response.get('Content-Type'), 'text/csv')

    def test_json_response(self):
        generator = ResponseFormatterGenerator('json').get_formatter()
        response = generator.run(self.query, {})

        self.assertEqual(response.get('Content-Type'), 'application/json')

    def test_csv_response_header_ids(self):
        generator = ResponseFormatterGenerator('csv').get_formatter()
        response = generator.run(self.query, {'header': 'ids'})
        line_end = response.content.find('\n')
        header = response.content[:line_end]
        self.assertTrue(self.single_series in header)

    def test_csv_response_header(self):
        generator = ResponseFormatterGenerator('csv').get_formatter()
        response = generator.run(self.query, {'header': 'names'})
        line_end = response.content.find('\n')
        header = response.content[:line_end]
        self.assertTrue(self.series_name in header)

    def test_csv_name(self):
        generator = ResponseFormatterGenerator('csv').get_formatter()
        response = generator.run(self.query, {})
        self.assertEquals(
            response.get('Content-Disposition'),
            'attachment; filename="{}"'.format(constants.CSV_RESPONSE_FILENAME)
        )
