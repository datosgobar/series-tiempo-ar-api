#! coding: utf-8
import json
import os

from django.test import TestCase
from django_datajsonar.models import Catalog
from django.core.files import File
from freezegun import freeze_time

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.indexing.indexer.metadata import update_enhanced_meta, _is_series_updated
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class FieldEnhancedMetaTests(TestCase):
    catalog_id = 'test_catalog'

    def setUp(self):
        Catalog.objects.all().delete()
        self.catalog = Catalog.objects.create(identifier=self.catalog_id)
        dataset = self.catalog.dataset_set.create(identifier="1")
        self.distribution_id = "1.1"
        distribution = dataset.distribution_set.create(identifier=self.distribution_id)
        distribution.field_set.create(title='indice_tiempo',
                                      identifier='indice_tiempo',
                                      metadata=json.dumps({"specialType": "time_index", "specialTypeDetail": "R/P1D"}),
                                      present=True)
        distribution.enhanced_meta.create(key=meta_keys.PERIODICITY, value='R/P1D')
        # Mismo title que dentro de la distribucion "daily_periodicity.csv"
        self.field = distribution.field_set.create(title='tasas_interes_call', identifier='test_series')

    def test_start_end_dates(self):
        df = self.init_df()

        update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        self.assertEqual(str(df.index[0].date()), meta_keys.get(self.field, meta_keys.INDEX_START))
        self.assertEqual(str(df.index[-1].date()), meta_keys.get(self.field, meta_keys.INDEX_END))

    def test_last_values(self):
        df = self.init_df()

        serie = df[df.columns[-1]]
        update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        self.assertEqual(meta_keys.get(self.field, meta_keys.LAST_VALUE), str(serie[-1]))
        self.assertEqual(meta_keys.get(self.field, meta_keys.SECOND_TO_LAST_VALUE), str(serie[-2]))

    def test_last_pct_change(self):
        df = self.init_df()

        serie = df[df.columns[-1]]
        update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        self.assertEqual(meta_keys.get(self.field, meta_keys.LAST_PCT_CHANGE), str(serie[-1] / serie[-2] - 1))

    def test_periodicity(self):
        df = self.init_df()
        update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        self.assertEqual(meta_keys.get(self.field, meta_keys.PERIODICITY),
                         meta_keys.get(self.field.distribution, meta_keys.PERIODICITY))

    def test_size(self):
        df = self.init_df()
        update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        self.assertEqual(meta_keys.get(self.field, meta_keys.INDEX_SIZE),
                         str(len(df)))

    def test_is_daily_series_updated(self):
        is_updated = _is_series_updated(days_since_last_update=1, periodicity="R/P1D")

        self.assertTrue(is_updated)

    def test_is_daily_series_not_updated(self):
        # Hasta dos semanas se considera como actualizada
        is_updated = _is_series_updated(days_since_last_update=15, periodicity="R/P1D")

        self.assertFalse(is_updated)

    @freeze_time("2018-01-01")
    def test_is_not_updated(self):
        df = self.init_df()
        update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        self.assertEqual(meta_keys.get(self.field, meta_keys.IS_UPDATED),
                         str(False))

    def test_is_updated(self):
        df = self.init_df()
        with freeze_time(df.index[-1]):
            update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)
        self.assertEqual(meta_keys.get(self.field, meta_keys.IS_UPDATED),
                         str(True))

    def test_max(self):
        df = self.init_df()
        update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        self.assertAlmostEqual(float(meta_keys.get(self.field, meta_keys.MAX)), df[df.columns[0]].max())

    def test_min(self):
        df = self.init_df()
        update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        self.assertAlmostEqual(float(meta_keys.get(self.field, meta_keys.MIN)), df[df.columns[0]].min())

    def test_average(self):
        df = self.init_df()
        update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        self.assertAlmostEqual(float(meta_keys.get(self.field, meta_keys.AVERAGE)), df[df.columns[0]].mean())

    def init_df(self):
        self.field.distribution.data_file = File(open(os.path.join(SAMPLES_DIR,
                                                                   'daily_periodicity.csv')))
        time_index = self.field.distribution.field_set.create(title="indice_tiempo",
                                                              identifier='indice_tiempo',
                                                              metadata=json.dumps({"specialType": "time_index",
                                                                                  "specialTypeDetail": "R/P1D"}))
        df = DistributionIndexer('test_index').init_df(
            self.field.distribution,
            time_index
        )
        return df
