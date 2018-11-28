from typing import Optional

from faker import Faker

from django.test import TestCase
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.dump.models import DumpFile, GenerateDumpTask

fake = Faker()


class DumpFileTests(TestCase):

    def setUp(self):
        GenerateDumpTask.objects.create()
        self.init_dumps_for_type(node=None)

        self.first_node = Node.objects.create(catalog_id=fake.pystr(),
                                              indexable=True,
                                              catalog_url=fake.pystr())
        self.init_dumps_for_type(self.first_node)
        self.second_node = Node.objects.create(catalog_id=fake.pystr(),
                                               indexable=True,
                                               catalog_url=fake.pystr())
        self.init_dumps_for_type(self.second_node)

    def create_dump_for_node(self, node, _type: str = DumpFile.TYPE_CSV, name: str = DumpFile.FILENAME_FULL):
        DumpFile.objects.create(node=node,
                                file_type=_type,
                                file_name=name,
                                task=GenerateDumpTask.objects.last())

    def init_dumps_for_type(self, node: Optional[Node], _type: str = DumpFile.TYPE_CSV):
        for name, _ in DumpFile.FILENAME_CHOICES:
            self.create_dump_for_node(node, _type, name)

    def test_get_global_dumps_node_is_none(self):
        dumps = DumpFile.get_last_of_type(DumpFile.TYPE_CSV, None)

        for dump in dumps:
            self.assertTrue(dump.node is None)

    def test_get_catalog_dumps(self):
        dumps = DumpFile.get_last_of_type(DumpFile.TYPE_CSV, self.first_node.catalog_id)
        for dump in dumps:
            self.assertEqual(dump.node.catalog_id, self.first_node.catalog_id)
