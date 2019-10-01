import mock
from django.test import TestCase
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.management.models import IndexDataTask
from series_tiempo_ar_api.apps.management.tasks.indexation import read_datajson
from series_tiempo_ar_api.libs.indexing.catalog_reader import index_catalog


@mock.patch('series_tiempo_ar_api.apps.management.tasks.indexation.index_catalog')
class DataIndexTaskTests(TestCase):
    def setUp(self):
        self.node_one = Node.objects.create(indexable=True,
                                            catalog_url="http://test_catalog.com",
                                            catalog_id='test_catalog')
        self.node_two = Node.objects.create(indexable=True,
                                            catalog_url="http://test_catalog_2.com",
                                            catalog_id='test_catalog_2')

    def test_indexation_is_called_once_for_one_node(self, indexation):
        task = IndexDataTask.objects.create(node=self.node_one)
        read_datajson(task)
        indexation.assert_called_once()
        indexation.assert_called_with(task.node, task, False, False)

    def test_indexation_is_called_for_all_nodes_if_task_created_without_nodes(self, indexation):
        task = IndexDataTask.objects.create()
        read_datajson(task)
        calls = indexation.call_count
        self.assertEquals(calls, 2)
