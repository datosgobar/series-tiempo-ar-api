import os
from random import shuffle

from django.core.management import call_command
from django.test import TestCase
from faker import Faker

from series_tiempo_ar_api.apps.dump.generator.xlsx.generator import generate, sort_key
from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask, DumpFile
from series_tiempo_ar_api.apps.dump.tasks import enqueue_write_xlsx_task
from series_tiempo_ar_api.utils.utils import index_catalog

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
        enqueue_write_xlsx_task()
        self.assertEqual(DumpFile.objects.filter(file_type=DumpFile.TYPE_XLSX, node=None).count(),
                         len(DumpFile.FILENAME_CHOICES))
        self.assertEqual(DumpFile.objects.filter(file_type=DumpFile.TYPE_XLSX, node__catalog_id='catalog_one').count(),
                         len(DumpFile.FILENAME_CHOICES))
        self.assertEqual(DumpFile.objects.filter(file_type=DumpFile.TYPE_XLSX, node__catalog_id='catalog_two').count(),
                         len(DumpFile.FILENAME_CHOICES))


class SheetSortTests(TestCase):

    class MockSheet:
        def __init__(self, name):
            self.name = name

        def __eq__(self, other):
            return self.name == other.name

    def test_sort_common_case(self):
        sheets = self.init_sheets(
            ['anual-1', 'trimestral-1', 'mensual-1', 'diaria-1', 'semestral-1', 'diaria-2']
        )
        shuffle(sheets)

        sheets.sort(key=sort_key)

        expected = self.init_sheets(['anual-1',
                                     'semestral-1',
                                     'trimestral-1',
                                     'mensual-1',
                                     'diaria-1',
                                     'diaria-2'])
        self.assertListEqual(sheets, expected)

    def test_sort(self):
        sheets = self.init_sheets([
            'anual-1',
            'trimestral-1',
            'mensual-1',
            'diaria-1',
            'semestral-1'
        ])

        shuffle(sheets)

        sheets.sort(key=sort_key)
        self.assertListEqual(sheets,
                             self.init_sheets(['anual-1', 'semestral-1', 'trimestral-1', 'mensual-1', 'diaria-1']))

    def test_sort_pages(self):
        sheets = self.init_sheets([
            'anual-1',
            'diaria-1',
            'diaria-2',
            'anual-2',
            'semestral-1'
        ])
        shuffle(sheets)

        sheets.sort(key=sort_key)
        self.assertListEqual(sheets, self.init_sheets(['anual-1', 'anual-2', 'semestral-1', 'diaria-1', 'diaria-2']))

    def init_sheets(self, names):
        return [self.MockSheet(name) for name in names]
