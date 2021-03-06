from django.test import TestCase
from django_datajsonar.models import Catalog

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.datajsonar_repositories.series_repository import SeriesRepository


class SeriesRepositoryTests(TestCase):

    def setUp(self):
        Catalog.objects.all().delete()
        catalog = Catalog.objects.create()
        dataset = catalog.dataset_set.create()
        self.distribution = dataset.distribution_set.create()

    def test_no_series_no_results(self):
        series = SeriesRepository.get_available_series()
        self.assertFalse(series)

    def test_no_available_series_no_results(self):
        self.distribution.field_set.create()
        series = SeriesRepository.get_available_series()
        self.assertFalse(series)

    def test_one_available_series_shows_up_in_result(self):
        field = self.distribution.field_set.create()
        field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
        series = SeriesRepository.get_available_series()
        self.assertTrue(series)

    def test_available_and_unavailable_series(self):
        self.distribution.field_set.create()
        available_field = self.distribution.field_set.create()
        available_field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
        series = SeriesRepository.get_available_series()
        self.assertEqual(series.count(), 1)

    def test_two_available_series(self):
        first_field = self.distribution.field_set.create()
        first_field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
        available_field = self.distribution.field_set.create()
        available_field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
        series = SeriesRepository.get_available_series()
        self.assertEqual(series.count(), 2)

    def test_non_present_series(self):
        non_present_field = self.distribution.field_set.create(present=False)
        non_present_field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
        series = SeriesRepository.get_available_series()
        self.assertTrue(series)

    def test_present_and_available_series(self):
        field = self.distribution.field_set.create()
        field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
        self.assertEqual(SeriesRepository.get_present_and_available_series().count(), 1)

    def test_present_and_available_series_non_present(self):
        non_present_field = self.distribution.field_set.create(present=False)
        non_present_field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
        series = SeriesRepository.get_present_and_available_series()
        self.assertFalse(series)

    def test_present_and_available_series_non_available(self):
        self.distribution.field_set.create(present=True)
        series = SeriesRepository.get_present_and_available_series()
        self.assertFalse(series)

    def test_custom_filter(self):
        field = self.distribution.field_set.create(title='test_title')
        field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
        other_field = self.distribution.field_set.create(title='other_title')
        other_field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
        series = SeriesRepository.get_available_series(title='test_title')
        self.assertEqual(series.count(), 1)
