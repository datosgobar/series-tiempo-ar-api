#! coding: utf-8
import os
import mock

from django_datajsonar.tasks import read_datajson
from django_datajsonar.models import Distribution, Field, Catalog
from django_datajsonar.models import ReadDataJsonTask, Node

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.management.models import IndexDataTask as ManagementTask, DistributionValidatorConfig
from series_tiempo_ar_api.libs.indexing.catalog_reader import index_catalog
from series_tiempo_ar_api.libs.indexing.tests.indexing_test_case import IndexingTestCase

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
CATALOG_ID = 'test_catalog'


@mock.patch("series_tiempo_ar_api.libs.indexing.tasks.DistributionIndexer.reindex")
class ReaderTests(IndexingTestCase):
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
        read_datajson(self.task, whitelist=True, )
        index_catalog(self.node, self.mgmt_task, )
        read_datajson(self.task, whitelist=True, )
        index_catalog(self.node, self.mgmt_task, )

        count = Field.objects.filter(identifier='212.1_PSCIOS_ERN_0_0_25').count()

        self.assertEqual(count, 1)

    def test_dont_index_same_distribution_twice(self, *_):
        read_datajson(self.task, whitelist=True, )
        index_catalog(self.node, self.mgmt_task, )
        read_datajson(self.task, whitelist=True, )
        index_catalog(self.node, self.mgmt_task, )

        distribution = Distribution.objects.get(identifier='212.1')

        # La distribucion es marcada como no indexable hasta que cambien sus datos
        self.assertEqual(distribution.enhanced_meta.get(key=meta_keys.CHANGED).value, 'False')

    def test_first_time_distribution_indexable(self, *_):
        read_datajson(self.task, whitelist=True, )
        index_catalog(self.node, self.mgmt_task,)

        distribution = Distribution.objects.get(identifier='212.1')

        self.assertEqual(distribution.enhanced_meta.get(key=meta_keys.CHANGED).value, 'True')

    def test_index_same_distribution_if_data_changed(self, *_):
        read_datajson(self.task, whitelist=True)
        index_catalog(self.node, self.mgmt_task)
        new_catalog = os.path.join(SAMPLES_DIR, 'full_ts_data_changed.json')
        self.node.catalog_url = new_catalog
        self.node.save()
        read_datajson(self.task, whitelist=True, )
        index_catalog(self.node, self.mgmt_task, )

        distribution = Distribution.objects.get(identifier='212.1')

        # La distribución fue indexada nuevamente, está marcada como indexable
        self.assertEqual(distribution.enhanced_meta.get(key=meta_keys.CHANGED).value, 'True')

    def test_error_distribution_logs(self, *_):
        catalog = os.path.join(SAMPLES_DIR, 'distribution_missing_downloadurl.json')
        self.node.catalog_url = catalog
        self.node.save()
        read_datajson(self.task, whitelist=True, )
        index_catalog(self.node, self.mgmt_task, )

        self.assertGreater(len(ReadDataJsonTask.objects.get(id=self.task.id).logs), 10)

    def test_index_YYYY_MM_distribution(self, *_):
        catalog = os.path.join(SAMPLES_DIR, 'single_data_yyyy_mm.json')
        self.node.catalog_url = catalog
        self.node.save()

        read_datajson(self.task, whitelist=True, )
        index_catalog(self.node, self.mgmt_task, )

        distribution = Distribution.objects.get(identifier='102.1')

        self.assertEqual(distribution.enhanced_meta.get(key=meta_keys.CHANGED).value, 'True')

    def test_index_YYYY_distribution(self, *_):
        catalog = os.path.join(SAMPLES_DIR, 'single_data_yyyy.json')
        self.node.catalog_url = catalog
        self.node.save()

        read_datajson(self.task, whitelist=True)
        index_catalog(self.node, self.mgmt_task)

        distribution = Distribution.objects.get(identifier='102.1')

        self.assertEqual(distribution.enhanced_meta.get(key=meta_keys.CHANGED).value, 'True')

    @mock.patch('series_tiempo_ar_api.libs.indexing.catalog_reader.DataJson')
    def test_format_is_passed_to_data_json(self, data_json, *_):
        read_datajson(self.task, whitelist=True)
        self.node.catalog_format = 'xlsx'
        index_catalog(self.node, self.mgmt_task)

        self.assertEqual(data_json.call_args[1]['catalog_format'], self.node.catalog_format)

    def test_significant_figures(self, *_):
        Catalog.objects.all().delete()
        catalog = os.path.join(SAMPLES_DIR, 'ipc_data.json')
        self.node.catalog_url = catalog
        self.node.save()

        read_datajson(self.task, whitelist=True)
        index_catalog(self.node, self.mgmt_task)

        field = Field.objects.get(identifier='serie_inflacion')  # Sacado del data.json
        self.assertEqual(field.enhanced_meta.get(key='significant_figures').value, '4')

    def test_custom_validation_options(self, *_):
        # Fallarán todas las validaciones
        config = DistributionValidatorConfig.get_solo()
        config.max_field_title_len = 0
        config.save()

        read_datajson(self.task, whitelist=True)
        index_catalog(self.node, self.mgmt_task)

        distribution = Distribution.objects.get(identifier='212.1')
        self.assertTrue(distribution.error)
