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

    def test_get_periodicity_reads_from_distribution_if_serie_has_none(self):
        self.field.enhanced_meta.all().delete()
        periodicity = SeriesQuery(self.field, constants.VALUE).periodicity()
        self.assertEqual(periodicity, 'month')

    def test_get_metadata_has_values_for_all_levels(self):
        meta = SeriesQuery(self.field, constants.VALUE).get_metadata()

        self.assertIn('catalog', meta)
        self.assertIn('dataset', meta)
        self.assertIn('distribution', meta)
        self.assertIn('field', meta)

    def test_get_metadata_flatten_has_description_in_first_level(self):
        meta = SeriesQuery(self.field, constants.VALUE).get_metadata(flat=True)
        self.assertIn('field_description', meta)
        self.assertNotIn('field', meta)

    def test_enhanced_meta_not_in_metadata_if_query_is_simple(self):
        meta = SeriesQuery(self.field, constants.VALUE).get_metadata(simple=True)

        self.assertNotIn('available', meta['field'])
