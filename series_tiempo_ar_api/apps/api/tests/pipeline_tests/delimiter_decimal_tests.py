#! coding: utf-8
from django.conf import settings
from django.test import TestCase

from django_datajsonar.models import Field
from series_tiempo_ar_api.apps.api.query.pipeline import Delimiter, DecimalChar
from series_tiempo_ar_api.apps.api.query.query import Query
from series_tiempo_ar_api.apps.api.tests.helpers import get_series_id


class DelimiterTests(TestCase):
    single_series = get_series_id('month')

    @classmethod
    def setUpClass(cls):
        cls.field = Field.objects.get(identifier=cls.single_series)
        super(cls, DelimiterTests).setUpClass()

    def setUp(self):
        self.query = Query(index=settings.TEST_INDEX)
        self.cmd = Delimiter()

    def test_delimiter(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'sep': '|'})

        self.assertFalse(self.cmd.errors)

    def test_multiple_delimiters(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'sep': '|;'})

        self.assertTrue(self.cmd.errors)


class DecimalCharTests(TestCase):
    single_series = get_series_id('month')

    @classmethod
    def setUpClass(cls):
        cls.field = Field.objects.get(identifier=cls.single_series)
        super(cls, DecimalCharTests).setUpClass()

    def setUp(self):
        self.query = Query(index=settings.TEST_INDEX)
        self.cmd = DecimalChar()

    def test_decimal_char(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'decimal': ','})

        self.assertFalse(self.cmd.errors)

    def test_multiple_decimal_chars(self):
        self.query.add_series(self.single_series, self.field, 'value')
        self.cmd.run(self.query, {'decimal': ',;'})

        self.assertTrue(self.cmd.errors)
