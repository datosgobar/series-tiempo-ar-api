import json
from datetime import datetime

from django.test import TestCase

from django_datajsonar.models import Field
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.series_query import SeriesQuery
from series_tiempo_ar_api.apps.api.tests.helpers import get_series_id


class SeriesQueryTests(TestCase):
    single_series = get_series_id('month')

    def setUp(self):
        self.field = Field.objects.get(identifier=self.single_series)
        self.field_description = "Mi descripción"
        self.field.metadata = json.dumps({'description': self.field_description})
        self.serie = SeriesQuery(self.field, constants.VALUE)

    def test_get_periodicity(self):
        periodicity = self.serie.periodicity()
        self.assertEqual(periodicity, 'month')

    def test_get_periodicity_reads_from_distribution_if_serie_has_none(self):
        self.field.enhanced_meta.all().delete()
        periodicity = SeriesQuery(self.field, constants.VALUE).periodicity()
        self.assertEqual(periodicity, 'month')

    def test_get_metadata_has_values_for_all_levels(self):
        meta = self.serie.get_metadata()

        self.assertIn('catalog', meta)
        self.assertIn('dataset', meta)
        self.assertIn('distribution', meta)
        self.assertIn('field', meta)

    def test_get_metadata_flatten_has_description_in_first_level(self):
        meta = self.serie.get_metadata(flat=True)
        self.assertIn('field_description', meta)
        self.assertNotIn('field', meta)

    def test_enhanced_meta_not_in_metadata_if_query_is_simple(self):
        meta = self.serie.get_metadata(simple=True)

        self.assertNotIn('available', meta['field'])

    def test_get_identifiers(self):
        ids = self.serie.get_identifiers()

        self.assertEqual(ids['id'], self.field.identifier)
        self.assertEqual(ids['distribution'], self.field.distribution.identifier)
        self.assertEqual(ids['dataset'], self.field.distribution.dataset.identifier)

    def test_get_title(self):
        title = self.serie.title()
        self.assertEqual(title, self.field.title)

    def test_get_description(self):
        description = self.serie.description()
        self.assertEqual(description, self.field_description)

    def test_get_description_no_description_set(self):
        self.field.metadata = json.dumps({})
        description = self.serie.description()
        self.assertEqual(description, '')

    def test_get_start_date(self):
        self.assertEqual(self.serie.start_date(), datetime(1910, 1, 1).date())

    def test_get_start_date_none_if_not_set(self):
        self.field.enhanced_meta.all().delete()
        self.assertEqual(self.serie.start_date(), None)
