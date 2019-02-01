#! coding: utf-8
import os
import mock

from django.core.files import File
from django.db import transaction
from django.test import TestCase
from elasticsearch_dsl import Search

from django_datajsonar.tasks import read_datajson
from django_datajsonar.models import Distribution, Field, Catalog
from django_datajsonar.models import ReadDataJsonTask, Node
from series_tiempo_ar_api.utils import utils
from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask as ManagementTask
from series_tiempo_ar_api.libs.indexing.catalog_reader import index_catalog
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
CATALOG_ID = 'test_catalog'


class IndexerTests(TestCase):
    test_index = 'indexer_test_index'

    @classmethod
    def setUpClass(cls):
        Catalog.objects.all().delete()
        cls.elastic = ElasticInstance()
        super(IndexerTests, cls).setUpClass()

    def test_init_dataframe_columns(self):
        self._index_catalog('full_ts_data.json')

        distribution = Distribution.objects.get(identifier="212.1")
        fields = distribution.field_set.all()
        fields = {field.title: field.identifier for field in fields}
        df = DistributionIndexer(self.test_index).init_df(distribution, fields)

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

    def test_index_all_zero_series(self):
        series_id = '212.1_todos_cero'
        self._index_catalog('ts_all_zero_series.json')

        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=series_id).execute()

        self.assertTrue(len(results))

    def test_catalog_value_indexed(self):
        self._index_catalog('distribution_daily_periodicity.json')

        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', catalog=CATALOG_ID).execute()

        self.assertTrue(len(results))

    def test_distribution_update(self):
        series_id = '102.1_I2NG_ABRI_M_22'
        self._index_catalog('single_data.json')

        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=series_id).execute()

        self.assertEqual(len(results), 2)

        node = Node.objects.get(catalog_id=CATALOG_ID)
        node.catalog_url = os.path.join(SAMPLES_DIR, 'single_data_updated.json')
        node.save()

        self._index_catalog('single_data_updated.json', node)

        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=series_id).execute()

        self.assertEqual(len(results), 3)

    def test_reindex_same_distribution(self):
        self._index_catalog('single_data.json')
        self.assertEqual(Field.objects.count(), 2)
        series_id = '102.1_I2NG_ABRI_M_22'
        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=series_id).execute()

        DistributionIndexer(index=self.test_index).reindex(Distribution.objects.first())
        updated_results = Search(using=self.elastic,
                                 index=self.test_index) \
            .filter('match', series_id=series_id).execute()

        # No cambia nada
        self.assertEqual(list(results), list(updated_results))

    def test_reindex_additional_value(self):
        self._index_catalog('single_data.json')
        self.assertEqual(Field.objects.count(), 2)
        series_id = '102.1_I2NG_ABRI_M_22'
        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=series_id).execute()

        self.assertEqual(len(list(results)), 2)
        distribution = Distribution.objects.get(identifier="102.1")
        distribution.data_file = File(open(os.path.join(SAMPLES_DIR, 'single_data_updated.csv'), 'rb'))
        distribution.save()
        DistributionIndexer(index=self.test_index).reindex(distribution)
        self.elastic.indices.forcemerge(index=self.test_index)
        updated_results = Search(using=self.elastic,
                                 index=self.test_index) \
            .filter('match', series_id=series_id).execute()
        self.assertEqual(len(list(updated_results)), 3)

        self.assertEqual(list(results), list(updated_results[:2]))

    def test_reindex_remove_value(self):
        self._index_catalog('single_data_updated.json')
        self.assertEqual(Field.objects.count(), 2)
        series_id = '102.1_I2NG_ABRI_M_22'
        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=series_id).execute()

        self.assertEqual(len(list(results)), 3)
        distribution = Distribution.objects.get(identifier="102.1")
        distribution.data_file = File(open(os.path.join(SAMPLES_DIR, 'single_data.csv'), 'rb'))
        distribution.save()
        DistributionIndexer(index=self.test_index).reindex(distribution)
        self.elastic.indices.forcemerge(index=self.test_index)
        updated_results = Search(using=self.elastic,
                                 index=self.test_index) \
            .filter('match', series_id=series_id).execute()
        self.assertEqual(len(list(updated_results)), 2)

        self.assertEqual(list(results[:2]), list(updated_results))

    def test_reindex_update_value(self):
        self._index_catalog('single_data.json')
        self.assertEqual(Field.objects.count(), 2)
        series_id = '102.1_I2NG_ABRI_M_22'
        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=series_id).execute()

        self.assertEqual(len(list(results)), 2)
        distribution = Distribution.objects.get(identifier="102.1")
        distribution.data_file = File(open(os.path.join(SAMPLES_DIR, 'single_data_value_changed.csv'), 'rb'))
        distribution.save()
        DistributionIndexer(index=self.test_index).reindex(distribution)
        self.elastic.indices.forcemerge(index=self.test_index)
        updated_results = Search(using=self.elastic,
                                 index=self.test_index) \
            .filter('match', series_id=series_id).execute()
        self.assertEqual(len(list(updated_results)), 2)

        self.assertEqual(list(results)[0], list(updated_results)[0])
        self.assertNotEqual(list(results)[1], list(updated_results)[1])

    def test_reindex_distribution_no_time_index_identifier(self):
        self._index_catalog('distribution_time_index_no_identifier.json')

        DistributionIndexer(index=self.test_index).reindex(Distribution.objects.first())
        series_id = '89.2_TS_INTEALL_0_D_18'
        results = Search(using=self.elastic,
                         index=self.test_index) \
            .filter('match', series_id=series_id).execute()

        self.assertTrue(list(results))

    def tearDown(self):
        if self.elastic.indices.exists(self.test_index):
            self.elastic.indices.delete(self.test_index)
        Distribution.objects.filter(dataset__catalog__identifier=CATALOG_ID).delete()
        Node.objects.all().delete()

    def _index_catalog(self, catalog_path, node=None):
        path = os.path.join(SAMPLES_DIR, catalog_path)
        utils.index_catalog(CATALOG_ID, path, self.test_index, node=node)


@mock.patch("series_tiempo_ar_api.libs.indexing.tasks.DistributionIndexer.reindex")
class ReaderTests(TestCase):
    catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
    catalog_id = 'catalog_id'

    def setUp(self):
        self.task = ReadDataJsonTask.objects.create()
        self.task.save()
        self.mgmt_task = ManagementTask()
        self.mgmt_task.save()
        self.node = Node(catalog_id=self.catalog_id, catalog_url=self.catalog, indexable=True)
        self.node.save()

    def test_index_same_series_different_catalogs(self, *_):
        read_datajson(self.task, whitelist=True, read_local=True)
        index_catalog(self.node, self.mgmt_task, read_local=True)
        read_datajson(self.task, whitelist=True, read_local=True)
        index_catalog(self.node, self.mgmt_task, read_local=True)

        count = Field.objects.filter(identifier='212.1_PSCIOS_ERN_0_0_25').count()

        self.assertEqual(count, 1)

    def test_dont_index_same_distribution_twice(self, *_):
        read_datajson(self.task, whitelist=True, read_local=True)
        index_catalog(self.node, self.mgmt_task, read_local=True)
        read_datajson(self.task, whitelist=True, read_local=True)
        index_catalog(self.node, self.mgmt_task, read_local=True)

        distribution = Distribution.objects.get(identifier='212.1')

        # La distribucion es marcada como no indexable hasta que cambien sus datos
        self.assertEqual(distribution.enhanced_meta.get(key=meta_keys.CHANGED).value, 'False')

    def test_first_time_distribution_indexable(self, *_):
        read_datajson(self.task, whitelist=True, read_local=True)
        index_catalog(self.node, self.mgmt_task, read_local=True, )

        distribution = Distribution.objects.get(identifier='212.1')

        self.assertEqual(distribution.enhanced_meta.get(key=meta_keys.CHANGED).value, 'True')

    def test_index_same_distribution_if_data_changed(self, *_):
        read_datajson(self.task, whitelist=True, read_local=True)
        index_catalog(self.node, self.mgmt_task, read_local=True, )
        new_catalog = os.path.join(SAMPLES_DIR, 'full_ts_data_changed.json')
        self.node.catalog_url = new_catalog
        self.node.save()
        read_datajson(self.task, whitelist=True, read_local=True)
        index_catalog(self.node, self.mgmt_task, read_local=True)

        distribution = Distribution.objects.get(identifier='212.1')

        # La distribución fue indexada nuevamente, está marcada como indexable
        self.assertEqual(distribution.enhanced_meta.get(key=meta_keys.CHANGED).value, 'True')

    def test_error_distribution_logs(self, *_):
        catalog = os.path.join(SAMPLES_DIR, 'distribution_missing_downloadurl.json')
        self.node.catalog_url = catalog
        self.node.save()
        read_datajson(self.task, whitelist=True, read_local=True)
        index_catalog(self.node, self.mgmt_task, read_local=True)

        self.assertGreater(len(ReadDataJsonTask.objects.get(id=self.task.id).logs), 10)
