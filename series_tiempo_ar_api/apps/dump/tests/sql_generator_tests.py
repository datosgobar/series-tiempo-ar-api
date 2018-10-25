import os

import peewee
from django.core.management import call_command
from django.test import TestCase
from django_datajsonar.models import Node, Catalog
from faker import Faker

from series_tiempo_ar_api.apps.dump.generator.sql.models import Serie, proxy
from series_tiempo_ar_api.apps.dump.generator.sql.generator import SQLGenerator
from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask, DumpFile
from series_tiempo_ar_api.apps.dump.tasks import enqueue_write_sql_task
from series_tiempo_ar_api.utils import index_catalog

samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class SQLGeneratorTests(TestCase):
    fake = Faker()
    index = fake.word()

    @classmethod
    def setUpClass(cls):
        super(SQLGeneratorTests, cls).setUpClass()
        Node.objects.all().delete()
        Catalog.objects.all().delete()
        GenerateDumpTask.objects.all().delete()
        DumpFile.objects.all().delete()

        path = os.path.join(samples_dir, 'distribution_daily_periodicity.json')
        index_catalog('catalog_one', path, index=cls.index)

        path = os.path.join(samples_dir, 'leading_nulls_distribution.json')
        index_catalog('catalog_two', path, index=cls.index)

        call_command('generate_dump')

    def test_sql_dumps_generated(self):
        task = GenerateDumpTask.objects.create()
        SQLGenerator(task.id).generate()

        self.assertTrue(DumpFile.objects.filter(file_type=DumpFile.TYPE_SQL).count())

    def test_sql_dumps_by_catalog(self):
        enqueue_write_sql_task()
        self.assertEqual(DumpFile.objects.filter(file_type=DumpFile.TYPE_SQL, node=None).count(),
                         1)
        self.assertEqual(DumpFile.objects.filter(file_type=DumpFile.TYPE_SQL, node__catalog_id='catalog_one').count(),
                         1)
        self.assertEqual(DumpFile.objects.filter(file_type=DumpFile.TYPE_SQL, node__catalog_id='catalog_two').count(),
                         1)
