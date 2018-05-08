#! coding: utf-8
import json
from django.conf import settings
from django.test import TestCase

from django_datajsonar.models import Field
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.query import Query
from series_tiempo_ar_api.apps.api.query.response import \
    ResponseFormatterGenerator
from .helpers import get_series_id

SERIES_NAME = get_series_id('month')


class ResponseTests(TestCase):
    single_series = SERIES_NAME

    @classmethod
    def setUpClass(cls):
        cls.query = Query(index=settings.TEST_INDEX)
        field = Field.objects.get(identifier=cls.single_series)
        cls.query.add_series(cls.single_series, field)
        cls.series_name = field.title
        cls.series_desc = json.loads(field.metadata)['description']
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
        line_end = str(response.content).find('\n')
        header = response.content[:line_end]
        self.assertTrue(self.single_series in str(header))

    def test_csv_response_header(self):
        generator = ResponseFormatterGenerator('csv').get_formatter()
        response = generator.run(self.query, {'header': 'titles'})
        line_end = str(response.content).find('\n')
        header = response.content[:line_end]
        self.assertTrue(self.series_name in str(header))

    def test_csv_name(self):
        generator = ResponseFormatterGenerator('csv').get_formatter()
        response = generator.run(self.query, {})
        self.assertEquals(
            response.get('Content-Disposition'),
            'attachment; filename="{}"'.format(constants.CSV_RESPONSE_FILENAME)
        )

    def test_csv_response_header_description(self):
        generator = ResponseFormatterGenerator('csv').get_formatter()
        response = generator.run(self.query, {'header': 'descriptions'})
        line_end = str(response.content).find('\n')
        header = response.content[:line_end]
        self.assertIn(self.series_desc, str(header))

    def test_csv_different_decimal_empty_rows(self):
        query = Query(index=settings.TEST_INDEX)

        field = Field.objects.get(identifier=self.single_series)
        query.add_series(self.single_series, field)
        query.add_series(self.single_series, field, rep_mode='percent_change_a_year_ago')

        generator = ResponseFormatterGenerator('csv').get_formatter()
        response = generator.run(query, {'decimal': ','})

        self.assertFalse("None" in str(response.content))
