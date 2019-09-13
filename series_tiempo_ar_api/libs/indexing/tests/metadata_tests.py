#! coding: utf-8
import os
import pandas as pd

from django.test import TestCase
from freezegun import freeze_time

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.indexing.indexer.metadata import calculate_enhanced_meta, _is_series_updated
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class FieldEnhancedMetaTests(TestCase):
    catalog_id = 'test_catalog'

    def setUp(self):
        self.periodicity = 'R/P1D'
        path = os.path.join(SAMPLES_DIR, 'daily_periodicity.csv')
        self.df = pd.read_csv(path, parse_dates=['indice_tiempo'], index_col='indice_tiempo')
        self.meta = calculate_enhanced_meta(self.df[self.df.columns[0]], self.periodicity)

    def test_start_end_dates(self):
        self.assertEqual(self.df.index[0].date(), self.meta.get(meta_keys.INDEX_START))
        self.assertEqual(self.df.index[-1].date(), self.meta.get(meta_keys.INDEX_END))

    def test_last_values(self):
        serie = self.df[self.df.columns[0]]

        self.assertEqual(self.meta.get(meta_keys.LAST_VALUE), serie[-1])
        self.assertEqual(self.meta.get(meta_keys.SECOND_TO_LAST_VALUE), serie[-2])

    def test_last_pct_change(self):
        serie = self.df[self.df.columns[0]]

        self.assertEqual(self.meta.get(meta_keys.LAST_PCT_CHANGE), serie[-1] / serie[-2] - 1)

    def test_periodicity(self):
        self.assertEqual(self.meta.get(meta_keys.PERIODICITY),
                         self.periodicity)

    def test_size(self):
        self.assertEqual(self.meta.get(meta_keys.INDEX_SIZE), len(self.df))

    def test_is_daily_series_updated(self):
        is_updated = _is_series_updated(days_since_last_update=1, periodicity="R/P1D")

        self.assertTrue(is_updated)

    def test_is_daily_series_not_updated(self):
        # Hasta dos semanas se considera como actualizada
        is_updated = _is_series_updated(days_since_last_update=15, periodicity="R/P1D")

        self.assertFalse(is_updated)

    @freeze_time("2018-01-01")
    def test_is_not_updated(self):
        meta = calculate_enhanced_meta(self.df[self.df.columns[0]], self.periodicity)
        self.assertFalse(meta.get(meta_keys.IS_UPDATED))

    def test_is_updated(self):
        with freeze_time(self.df.index[-1]):
            meta = calculate_enhanced_meta(self.df[self.df.columns[0]], self.periodicity)
        self.assertTrue(meta.get(meta_keys.IS_UPDATED))

    def test_max(self):
        self.assertAlmostEqual(self.meta.get(meta_keys.MAX), self.df[self.df.columns[0]].max())

    def test_min(self):
        self.assertAlmostEqual(self.meta.get(meta_keys.MIN), self.df[self.df.columns[0]].min())

    def test_average(self):
        self.assertAlmostEqual(self.meta.get(meta_keys.AVERAGE), self.df[self.df.columns[0]].mean())

    def test_significant_figures(self):
        serie_figures = 4  # primera serie tiene a lo sumo 4 decimales
        self.assertAlmostEqual(self.meta.get(meta_keys.SIGNIFICANT_FIGURES), serie_figures)
