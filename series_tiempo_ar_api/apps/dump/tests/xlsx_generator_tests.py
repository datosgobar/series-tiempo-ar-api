import os

from django.core.files.temp import NamedTemporaryFile
from django.core.management import call_command
from django.test import TestCase
from faker import Faker

from series_tiempo_ar_api.apps.dump.generator.xlsx.generator import generate
from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask, DumpFile
from series_tiempo_ar_api.utils import index_catalog

samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class XLSXGeneratorTests(TestCase):
    fake = Faker()
    index = fake.word()

    @classmethod
    def setUpClass(cls):
        super(XLSXGeneratorTests, cls).setUpClass()
        GenerateDumpTask.objects.all().delete()
        DumpFile.objects.all().delete()

        path = os.path.join(samples_dir, 'distribution_daily_periodicity.json')
        index_catalog('catalog_one', path, index=cls.index)

        path = os.path.join(samples_dir, 'leading_nulls_distribution.json')
        index_catalog('catalog_two', path, index=cls.index)

        call_command('generate_dump')

    def test_xlsx_dumps_generated(self):
        task = GenerateDumpTask.objects.create()
        generate(task)

        self.assertTrue(DumpFile.objects.filter(file_type=DumpFile.TYPE_XLSX).count())

    def test_xlsx_dumps_by_catalog(self):
        task = GenerateDumpTask.objects.create()
        generate(task)
        generate(task, "catalog_one")
        generate(task, "catalog_two")
        self.assertEqual(DumpFile.objects.filter(file_type=DumpFile.TYPE_XLSX, node=None).count(),
                         len(DumpFile.FILENAME_CHOICES))
        self.assertEqual(DumpFile.objects.filter(file_type=DumpFile.TYPE_XLSX, node__catalog_id='catalog_one').count(),
                         len(DumpFile.FILENAME_CHOICES))
        self.assertEqual(DumpFile.objects.filter(file_type=DumpFile.TYPE_XLSX, node__catalog_id='catalog_two').count(),
                         len(DumpFile.FILENAME_CHOICES))
