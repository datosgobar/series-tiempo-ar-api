#! coding: utf-8
from django.conf import settings
from django.test import TestCase

from series_tiempo_ar_api.apps.api.query.pipeline import Collapse
from series_tiempo_ar_api.apps.api.query.query import Query
from series_tiempo_ar_api.apps.api.tests import setup_database
from ..helpers import get_series_id

SERIES_NAME = get_series_id('month')


class CollapseTest(TestCase):
    single_series = SERIES_NAME

    @classmethod
    def setUpClass(cls):
        super(cls, CollapseTest).setUpClass()

    def setUp(self):
        self.query = Query(index=settings.TEST_INDEX)
        self.cmd = Collapse()

    def test_valid_aggregation(self):
        self.cmd.run(self.query, {'ids': self.single_series,
                                  'collapse': 'year',
                                  'collapse_aggregation': 'sum'})
        self.assertFalse(self.cmd.errors)

    def test_invalid_collapse(self):
        self.cmd.run(self.query, {'ids': self.single_series,
                                  'collapse': 'invalid',
                                  'collapse_aggregation': 'sum'})

        self.assertTrue(self.cmd.errors)

    def test_semester_valid_aggregation(self):
        self.cmd.run(self.query, {'ids': self.single_series,
                                  'collapse': 'semester'})

        self.assertFalse(self.cmd.errors)
