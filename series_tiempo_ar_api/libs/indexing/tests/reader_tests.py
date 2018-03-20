#! coding: utf-8
import json
import os

from django.db import transaction
from django.test import TestCase
from elasticsearch_dsl import Search
from pydatajson import DataJson
from redis import Redis
from series_tiempo_ar.search import get_time_series_distributions

from series_tiempo_ar_api.apps.api.models import Distribution, Field, Catalog, Dataset
from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask, Node, Indicator
from series_tiempo_ar_api.libs.indexing.catalog_reader import index_catalog
from series_tiempo_ar_api.libs.indexing.database_loader import \
    DatabaseLoader
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer
from series_tiempo_ar_api.libs.indexing.report.indicators import IndicatorLoader

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
CATALOG_ID = 'test_catalog'


class IndexerTests(TestCase):
    test_index = 'indexer_test_index'

    @classmethod
    def setUpClass(cls):
        cls.elastic = ElasticInstance()

    def setUp(self):
        self.task = ReadDataJsonTask()
        self.task.save()

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

        node = Node(catalog_id=CATALOG_ID,
                    catalog_url=os.path.join(SAMPLES_DIR, 'full_ts_data.json'),
                    indexable=True)
        self._index_catalog('full_ts_data.json', node)
        with transaction.atomic():
            node.catalog_url = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
            # Segunda corrida, 'actualización' del catálogo
            self._index_catalog('missing_field.json', node)

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
        Distribution.objects.filter(dataset__catalog__identifier=CATALOG_ID).delete()

    def _index_catalog(self, catalog_path, node=None):
        if not node:
            node = Node(catalog_id=CATALOG_ID,
                        catalog_url=os.path.join(SAMPLES_DIR, catalog_path),
                        indexable=True)
        node.save()
        catalog = DataJson(json.loads(node.catalog))
        catalog_model, created = Catalog.objects.get_or_create(identifier=node.catalog_id)
        if created:
            catalog_model.title = catalog['title'],
            catalog_model.metadata = '{}'
            catalog_model.save()
        for dataset in catalog.get_datasets(only_time_series=True):
            dataset_model, created = Dataset.objects.get_or_create(
                catalog=catalog_model,
                identifier=dataset['identifier']
            )
            if created:
                dataset_model.metadata = '{}'
                dataset_model.indexable = True
                dataset_model.save()

        distributions = get_time_series_distributions(catalog)
        db_loader = DatabaseLoader(self.task, read_local=True, default_whitelist=True)
        for distribution in distributions:
            db_loader.run(distribution, catalog, CATALOG_ID)

        for distribution in Distribution.objects.filter(dataset__catalog__identifier=CATALOG_ID):
            DistributionIndexer(index=self.test_index).run(distribution)


class ReaderTests(TestCase):
    catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
    catalog_id = 'catalog_id'

    def setUp(self):
        self.task = ReadDataJsonTask.objects.create()
        self.node = Node(catalog_id=self.catalog_id, catalog_url=self.catalog, indexable=True)
        self.node.save()

    def test_index_same_series_different_catalogs(self):
        index_catalog(self.node, self.task, read_local=True, whitelist=True)
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        count = Field.objects.filter(series_id='212.1_PSCIOS_ERN_0_0_25').count()

        self.assertEqual(count, 1)

    def test_dont_index_same_distribution_twice(self):
        index_catalog(self.node, self.task, read_local=True, whitelist=True)
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        distribution = Distribution.objects.get(identifier='212.1')

        # La distribucion es marcada como no indexable hasta que cambien sus datos
        self.assertFalse(distribution.indexable)

    def test_first_time_distribution_indexable(self):
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        distribution = Distribution.objects.get(identifier='212.1')

        self.assertTrue(distribution.indexable)

    def test_index_same_distribution_if_data_changed(self):
        index_catalog(self.node, self.task, read_local=True, whitelist=True)
        new_catalog = os.path.join(SAMPLES_DIR, 'full_ts_data_changed.json')
        self.node.catalog_url = new_catalog
        self.node.save()
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        distribution = Distribution.objects.get(identifier='212.1')

        # La distribución fue indexada nuevamente, está marcada como indexable
        self.assertTrue(distribution.indexable)

    def test_error_distribution_logs(self):
        catalog = os.path.join(SAMPLES_DIR, 'distribution_missing_downloadurl.json')
        self.node.catalog_url = catalog
        self.node.save()
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        self.assertGreater(len(ReadDataJsonTask.objects.get(id=self.task.id).logs), 10)


class IndicatorsTests(TestCase):
    catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
    catalog_id = 'catalog_id'

    def setUp(self):
        self.loader = IndicatorLoader()
        self.loader.clear_indicators()  # Just in case
        self.task = ReadDataJsonTask.objects.create()
        self.node = Node(catalog_id=self.catalog_id, catalog_url=self.catalog, indexable=True)
        self.node.save()

    def test_error_distribution_indicator(self):
        self.loader.clear_indicators()
        catalog = os.path.join(SAMPLES_DIR, 'distribution_missing_downloadurl.json')
        self.node.catalog_url = catalog
        self.node.save()
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        indicator = int(self.loader.get(self.catalog_id, Indicator.DISTRIBUTION_ERROR))
        self.assertEqual(indicator, 1)
        indicator = int(self.loader.get(self.catalog_id, Indicator.FIELD_ERROR))
        self.assertEqual(indicator, 3)

        error = Dataset.objects.get(catalog__identifier=self.catalog_id).error
        self.assertTrue(error)

    def test_dataset_updated(self):
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        self.loader.clear_indicators()
        catalog = os.path.join(SAMPLES_DIR, 'full_ts_data_changed.json')
        self.node.catalog_url = catalog
        self.node.save()
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        indicator = int(self.loader.get(self.catalog_id, Indicator.DATASET_UPDATED))
        self.assertEqual(1, indicator)

    def tearDown(self):
        IndicatorLoader().clear_indicators()
