import os

from django.core.files import File
from django.test import TestCase
from django_datajsonar.models import Node
from django_rq import job
from faker import Faker

from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask, DumpFile, ZipDumpFile
from series_tiempo_ar_api.apps.dump.writer import Writer


fake = Faker()


def mock_dump_write(task: GenerateDumpTask, node: str):
    with open('test_file', 'w+b') as f:
        dump_file = DumpFile.objects.create(task=task,
                                            node=Node.objects.get(catalog_id=node) if node is not None else None,
                                            file_type=DumpFile.TYPE_CSV,
                                            file_name=DumpFile.FILENAME_METADATA,
                                            file=File(f))

    ZipDumpFile.create_from_dump_file(dump_file, 'test_file')
    os.remove('test_file')


@job
def init_writer(task_id: int, catalog_id: str = None):
    Writer(dump_type=DumpFile.TYPE_CSV,
           action=mock_dump_write,
           recursive_task=init_writer,
           task=task_id,
           catalog=catalog_id).write()


class WriterTests(TestCase):
    def test_write_dump(self):
        task = GenerateDumpTask.objects.create()
        init_writer(task.id)
        self.assertEqual(DumpFile.objects.count(), 1)

    def test_auto_delete_old_dumps(self):
        for i in range(10):
            task = GenerateDumpTask.objects.create()
            init_writer(task.id)

        self.assertEqual(DumpFile.objects.count(), constants.OLD_DUMP_FILES_AMOUNT)

    def test_catalog_dump(self):
        node = Node.objects.create(catalog_id=fake.name(),
                                   catalog_url=fake.url(),
                                   indexable=True)
        task = GenerateDumpTask.objects.create()
        init_writer(task.id)
        self.assertEqual(DumpFile.objects.filter(node=node).count(), 1)
        self.assertEqual(DumpFile.objects.filter(node=None).count(), 1)

    def test_zip_dumps(self):
        task = GenerateDumpTask.objects.create()
        init_writer(task.id)
        self.assertEqual(ZipDumpFile.objects.count(), 1)

    def test_auto_delete_zip_dumps(self):
        for i in range(10):
            task = GenerateDumpTask.objects.create()
            init_writer(task.id)

        self.assertEqual(ZipDumpFile.objects.count(), constants.OLD_DUMP_FILES_AMOUNT)
