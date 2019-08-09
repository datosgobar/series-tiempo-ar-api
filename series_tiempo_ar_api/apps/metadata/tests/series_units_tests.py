from django.test import TestCase

from series_tiempo_ar_api.apps.metadata.models import SeriesUnits


class SeriesUnitsTests(TestCase):

    def test_is_percentage_no_units(self):
        self.assertFalse(SeriesUnits.is_percentage('non_existent_units'))

    def test_is_percentage_units_exists_and_tagged_as_percentage(self):
        SeriesUnits.objects.create(name='pct_units', percentage=True)
        self.assertTrue(SeriesUnits.is_percentage('pct_units'))

    def test_is_percentage_units_exists_and_not_tagged_as_not_percentage(self):
        SeriesUnits.objects.create(name='non_pct_units', percentage=False)
        self.assertFalse(SeriesUnits.is_percentage('non_pct_units'))

    def test_default_is_not_percentage(self):
        SeriesUnits.objects.create(name='non_pct_units')
        self.assertFalse(SeriesUnits.is_percentage('non_pct_units'))
