from django.test import TestCase
from mock import patch
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer import run_metadata_indexer
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask


@patch('series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer.CatalogMetadataIndexer')
class RunMetadataIndexerTests(TestCase):

    def setUp(self):
        self.task = IndexMetadataTask.objects.create()
        Node.objects.create(indexable=True, catalog_url="http://test_catalog.com", catalog_id='test_catalog')
        Node.objects.create(indexable=True, catalog_url="http://test_catalog_2.com", catalog_id='test_catalog_2')

    def test_run_metadata_indexer_with_no_args_calls_indexer_for_all_nodes(self, catalog_indexer):
        catalog_indexer().index.return_value = False

        run_metadata_indexer(self.task)

        self.assertEqual(catalog_indexer().index.call_count, Node.objects.count())

    def test_run_metadata_indexer_for_single_node(self, catalog_indexer):
        catalog_indexer().index.return_value = False

        new_node = Node.objects.create(
            indexable=True,
            catalog_url="http://test_catalog_3.com",
            catalog_id='test_catalog_3')

        self.task.node = new_node
        self.task.save()
        run_metadata_indexer(self.task)

        self.assertIn(new_node, catalog_indexer.call_args[0])
        self.assertEqual(catalog_indexer().index.call_count, 1)
