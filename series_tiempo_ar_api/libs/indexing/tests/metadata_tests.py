#! coding: utf-8
import os
import datetime

import mock
from django.test import TransactionTestCase
from django_datajsonar.models import Catalog
from django.core.files import File

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.indexing.indexer.metadata import update_enhanced_meta
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class FieldEnhancedMetaTests(TransactionTestCase):
    catalog_id = 'test_catalog'

    def setUp(self):
        self.catalog = Catalog.objects.create(identifier=self.catalog_id)
        dataset = self.catalog.dataset_set.create(identifier="1")
        self.distribution_id = "1.1"
        distribution = dataset.distribution_set.create(identifier=self.distribution_id)
        distribution.enhanced_meta.create(key=meta_keys.PERIODICITY, value='R/P1D')
        self.field = distribution.field_set.create(identifier='test_series')

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

    def test_days_since_last_update(self):
        df = self.init_df()
        update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        last_date = df.index[-1]

        # Sólo válido porque la serie es diaria! Con otra periodicity hay que considerar
        # el fin del período
        days = (datetime.datetime.today() - last_date).days

        self.assertEqual(meta_keys.get(self.field, meta_keys.DAYS_SINCE_LAST_UPDATE),
                         str(days))

    class MockDatetime():
        def __init__(self, date):
            self.date = date

        def now(self):
            return self.date

    def test_is_not_updated(self):
        df = self.init_df()
        with mock.patch('series_tiempo_ar_api.libs.indexing.indexer.metadata.datetime',
                        self.MockDatetime(datetime.datetime(2018, 1, 1))):
            update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)

        self.assertEqual(meta_keys.get(self.field, meta_keys.IS_UPDATED),
                         str(False))

    def test_is_updated(self):
        df = self.init_df()
        with mock.patch('series_tiempo_ar_api.libs.indexing.indexer.metadata.datetime', self.MockDatetime(df.index[-1])):
            update_enhanced_meta(df[df.columns[0]], self.catalog_id, self.distribution_id)
        self.assertEqual(meta_keys.get(self.field, meta_keys.IS_UPDATED),
                         str(True))

    def init_df(self):
        self.field.distribution.data_file = File(open(os.path.join(SAMPLES_DIR,
                                                                   'daily_periodicity.csv')))
        self.field.distribution.field_set.create(identifier='indice_tiempo',
                                                 metadata='{"specialTypeDetail": "R/P1D"}')
        df = DistributionIndexer('test_index').init_df(
            self.field.distribution,
            {'tasas_interes_call': self.field.identifier,
             'indice_tiempo': 'indice_tiempo'}
        )
        return df
