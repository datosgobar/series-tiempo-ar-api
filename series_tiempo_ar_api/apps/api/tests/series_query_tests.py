from django.test import TestCase

from django_datajsonar.models import Field
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.series_query import SeriesQuery
from series_tiempo_ar_api.apps.api.tests.helpers import get_series_id


class SeriesQueryTests(TestCase):
    single_series = get_series_id('month')

    @classmethod
    def setUpTestData(cls):
        cls.field = Field.objects.get(identifier=cls.single_series)

    def test_get_periodicity(self):
        periodicity = SeriesQuery(self.field, constants.VALUE).periodicity()
        self.assertEqual(periodicity, 'month')
