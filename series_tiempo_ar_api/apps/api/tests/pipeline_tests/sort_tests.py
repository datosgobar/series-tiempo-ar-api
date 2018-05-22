#! coding: utf-8
from django.conf import settings
from django.test import TestCase
from iso8601 import iso8601

from django_datajsonar.models import Field
from series_tiempo_ar_api.apps.api.query.pipeline import Sort
from series_tiempo_ar_api.apps.api.query.query import Query
from ..helpers import get_series_id

SERIES_NAME = get_series_id('month')


class SortTests(TestCase):

    single_series = SERIES_NAME

    @classmethod
    def setUpClass(cls):
        cls.field = Field.objects.get(identifier=SERIES_NAME)
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
        self.query.add_collapse('year')
        data = self.query.run()['data']

        previous = iso8601.parse_date(data[0][0])
        for row in data[1:]:
            current = iso8601.parse_date(row[0])
            self.assertGreater(current, previous)
            previous = current

    def test_invalid_sort(self):
        self.cmd.run(self.query, {'sort': 'invalid'})
        self.assertTrue(self.cmd.errors)
