from django.test import TestCase
from django_datajsonar.models import Catalog
from faker import Faker

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.metadata.indexer.units import update_units
from series_tiempo_ar_api.apps.metadata.models import SeriesUnits


class UpdateUnitsTests(TestCase):
    faker = Faker()

    def setUp(self):
        self.test_units = self.faker.pystr()
        Catalog.objects.all().delete()
        catalog = Catalog.objects.create()
        dataset = catalog.dataset_set.create()
        self.distribution = dataset.distribution_set.create()
        field = self.distribution.field_set.create(metadata=f'{{"units": "{self.test_units}"}}')
        field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')

    def test_units_created(self):
        update_units()
        self.assertEqual(SeriesUnits.objects.get().name, self.test_units)

    def test_units_updated_both_exist(self):
        update_units()
        self.distribution.field_set.all().update(metadata='{"units": "new_units"}')
        update_units()
        self.assertEqual(SeriesUnits.objects.count(), 2)

    def test_two_units_creates_two_models(self):
        other_field = self.distribution.field_set.create(metadata='{"units": "other_units"}')
        other_field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
        update_units()
        self.assertEqual(SeriesUnits.objects.count(), 2)

    def test_once_deleted_series_units_still_exist(self):
        update_units()
        self.distribution.field_set.all().delete()
        update_units()
        self.assertEqual(SeriesUnits.objects.count(), 1)

    def test_run_no_changes_no_new_units(self):
        update_units()
        self.assertEqual(SeriesUnits.objects.get().name, self.test_units)
        update_units()
        self.assertEqual(SeriesUnits.objects.get().name, self.test_units)
