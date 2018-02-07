#! coding: utf-8
import json
import os

from django.conf import settings
from django.test import TestCase
from elasticsearch_dsl import Search
from series_tiempo_ar.search import get_time_series_distributions

from series_tiempo_ar_api.apps.api.indexing.database_loader import \
    DatabaseLoader
from series_tiempo_ar_api.apps.api.indexing.distribution_indexer import DistributionIndexer
from series_tiempo_ar_api.apps.api.indexing.scraping import Scraper
from series_tiempo_ar_api.apps.api.models import Distribution, Field, Catalog
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance
from series_tiempo_ar_api.apps.api.indexing.catalog_reader import index_catalog
from series_tiempo_ar_api.apps.api.tests import setup_database

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
CATALOG_ID = 'test_catalog'


class ScrapperTests(TestCase):
    def setUp(self):
        self.scrapper = Scraper(read_local=True)

    def test_scrapper(self):
        catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
        self.scrapper.run(catalog)

        self.assertTrue(len(self.scrapper.distributions))

    def test_missing_metadata_field(self):
        """No importa que un field no esté en metadatos, se scrapea
        igual, para obtener todas las series posibles
        """

        catalog = os.path.join(SAMPLES_DIR, 'missing_field.json')
        self.scrapper.run(catalog)
        self.assertTrue(len(self.scrapper.distributions))

    def test_missing_dataframe_column(self):
        """Si falta una columna indicada por los metadatos, no se
        scrapea la distribución
        """

        catalog = os.path.join(
            SAMPLES_DIR, 'distribution_missing_column.json'
        )
        self.scrapper.run(catalog)
        self.assertFalse(len(self.scrapper.distributions))


class IndexerTests(TestCase):
    test_index = 'indexer_test_index'

    @classmethod
    def setUpClass(cls):
        cls.elastic = ElasticInstance()

    def test_init_dataframe_columns(self):
        self._index_catalog('full_ts_data.json')

        distribution = Distribution.objects.get(identifier="212.1")
        fields = distribution.field_set.all()
        fields = {field.title: field.series_id for field in fields}
        df = DistributionIndexer.init_df(distribution, fields)

        for field in fields.values():
            self.assertTrue(field in df.columns)

    def test_indexing(self):
        self._index_catalog('full_ts_data.json')

        results = Search(using=self.elastic,
                         index=self.test_index).execute()
        self.assertTrue(len(results))

    def test_missing_field_update(self):
        """Al actualizar una distribución, si falta un field
        previamente indexado, no se borran los datos anteriores
        """
        missing_field = '212.1_PSCIOS_ERS_0_0_22'

        self._index_catalog('full_ts_data.json')
        # Segunda corrida, 'actualización' del catálogo
        self._index_catalog('missing_field.json')

        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=missing_field).execute()

        self.assertTrue(len(results))

    def test_distribution_missing_column(self):
        missing_series_id = '212.1_PSCIOS_IOS_0_0_25'
        self._index_catalog('distribution_missing_column.json')

        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=missing_series_id).execute()

        self.assertFalse(len(results))

    def test_index_daily_distribution(self):
        series_id = '89.2_TS_INTELAR_0_D_20'
        self._index_catalog('distribution_daily_periodicity.json')

        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=series_id).execute()

        self.assertTrue(len(results))

    @classmethod
    def tearDownClass(cls):
        pass

    def tearDown(self):
        if self.elastic.indices.exists(self.test_index):
            self.elastic.indices.delete(self.test_index)

    def _index_catalog(self, catalog_path):
        catalog = os.path.join(SAMPLES_DIR, catalog_path)
        distributions = get_time_series_distributions(catalog)
        db_loader = DatabaseLoader(read_local=True, default_whitelist=True)
        db_loader.run(catalog, CATALOG_ID, distributions)
        for distribution in db_loader.distribution_models:
            DistributionIndexer(index=self.test_index).run(distribution)


class DatabaseLoaderTests(TestCase):

    def setUp(self):
        setup_database()
        self.loader = DatabaseLoader(read_local=True, default_whitelist=True)

    def tearDown(self):
        Catalog.objects.all().delete()

    def test_blacklisted_catalog_meta(self):
        catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
        distributions = get_time_series_distributions(catalog)

        self.loader.run(catalog, CATALOG_ID, distributions)
        meta = self.loader.distribution_models[0].dataset.catalog.metadata
        meta = json.loads(meta)
        for field in settings.CATALOG_BLACKLIST:
            self.assertTrue(field not in meta)

    def test_blacklisted_dataset_meta(self):
        catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
        distributions = get_time_series_distributions(catalog)

        self.loader.run(catalog, CATALOG_ID, distributions)
        for distribution in self.loader.distribution_models:
            meta = distribution.dataset.metadata
            meta = json.loads(meta)
            for field in settings.DATASET_BLACKLIST:
                self.assertTrue(field not in meta)

    def test_blacklisted_distrib_meta(self):
        catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
        distributions = get_time_series_distributions(catalog)

        self.loader.run(catalog, CATALOG_ID, distributions)

        for distribution in self.loader.distribution_models:
            meta = distribution.metadata
            meta = json.loads(meta)
            for field in settings.DISTRIBUTION_BLACKLIST:
                self.assertTrue(field not in meta)

    def test_blacklisted_field_meta(self):
        catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
        distributions = get_time_series_distributions(catalog)

        self.loader.run(catalog, CATALOG_ID, distributions)

        for distribution in self.loader.distribution_models:
            for field_model in distribution.field_set.all():
                for field in settings.FIELD_BLACKLIST:
                    self.assertTrue(field not in field_model.metadata)

    def test_datasets_loaded_are_not_indexable(self):

        catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
        distributions = get_time_series_distributions(catalog)
        loader = DatabaseLoader(read_local=True, default_whitelist=False)
        loader.run(catalog, CATALOG_ID, distributions)
        dataset = Catalog.objects.get(identifier=CATALOG_ID).dataset_set

        self.assertEqual(dataset.count(), 1)
        self.assertFalse(dataset.first().indexable)


class ReaderTests(TestCase):
    catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')

    def test_index_same_series_different_catalogs(self):
        index_catalog(self.catalog, 'one_catalog_id', read_local=True, whitelist=True, async=False)
        index_catalog(self.catalog, 'other_catalog_id', read_local=True, whitelist=True, async=False)

        count = Field.objects.filter(series_id='212.1_PSCIOS_ERN_0_0_25').count()

        self.assertEqual(count, 1)

    def test_dont_index_same_distribution_twice(self):
        index_catalog(self.catalog, 'one_catalog_id', read_local=True, whitelist=True, async=False)
        index_catalog(self.catalog, 'one_catalog_id', read_local=True, whitelist=True, async=False)

        distribution = Distribution.objects.get(identifier='212.1')

        # La distribucion es marcada como no indexable hasta que cambien sus datos
        self.assertFalse(distribution.indexable)

    def test_first_time_distribution_indexable(self):
        index_catalog(self.catalog, 'one_catalog_id', read_local=True, whitelist=True, async=False)

        distribution = Distribution.objects.get(identifier='212.1')

        self.assertTrue(distribution.indexable)

    def test_index_same_distribution_if_data_changed(self):
        index_catalog(self.catalog, 'one_catalog_id', read_local=True, whitelist=True, async=False)
        new_catalog = os.path.join(SAMPLES_DIR, 'full_ts_data_changed.json')
        index_catalog(new_catalog, 'one_catalog_id', read_local=True, whitelist=True, async=False)

        distribution = Distribution.objects.get(identifier='212.1')

        # La distribución fue indexada nuevamente, está marcada como indexable
        self.assertTrue(distribution.indexable)
