import os

import peewee
from django.core.files.temp import NamedTemporaryFile
from django.core.management import call_command
from django.test import TestCase
from django_datajsonar.models import Node, Catalog, Field, Distribution
from elasticsearch_dsl.connections import connections
from faker import Faker

from series_tiempo_ar_api.apps.dump.generator.sql.models import Metadatos, proxy, Valores
from series_tiempo_ar_api.apps.dump.generator.sql.generator import SQLGenerator
from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask, DumpFile
from series_tiempo_ar_api.apps.dump.tasks import enqueue_write_sql_task
from series_tiempo_ar_api.libs.indexing.popularity import update_popularity_metadata
from series_tiempo_ar_api.utils.utils import index_catalog

samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class SQLGeneratorTests(TestCase):
    fake = Faker()
    index = fake.word()

    @classmethod
    def setUpClass(cls):
        super(SQLGeneratorTests, cls).setUpClass()
        DumpFile.objects.all().delete()
        Node.objects.all().delete()
        Catalog.objects.all().delete()
        GenerateDumpTask.objects.all().delete()

        path = os.path.join(samples_dir, 'distribution_daily_periodicity.json')
        index_catalog('catalog_one', path, index=cls.index)

        path = os.path.join(samples_dir, 'leading_nulls_distribution.json')
        index_catalog('catalog_two', path, index=cls.index)
        for distribution in Distribution.objects.all():
            update_popularity_metadata(distribution)

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

    @classmethod
    def tearDownClass(cls):
        super(SQLGeneratorTests, cls).tearDownClass()
        connections.get_connection().indices.delete(cls.index)


class SQLTests(TestCase):
    fake = Faker()
    index = fake.pystr(max_chars=50).lower()

    @classmethod
    def setUpClass(cls):
        super(SQLTests, cls).setUpClass()
        DumpFile.objects.all().delete()
        Node.objects.all().delete()
        Catalog.objects.all().delete()
        GenerateDumpTask.objects.all().delete()

        path = os.path.join(samples_dir, 'distribution_daily_periodicity.json')
        index_catalog('catalog_one', path, index=cls.index)

        call_command('generate_dump')
        task = GenerateDumpTask.objects.create()
        SQLGenerator(task.id).generate()

    def setUp(self):
        self.init_db()

    def test_table_rows(self):
        self.assertEqual(Metadatos.select().count(),
                         Field.objects.exclude(title='indice_tiempo').count())

    def test_foreign_key(self):
        serie = Metadatos.select().first()
        values = Valores.filter(serie_id=serie)
        self.assertTrue(values)

    def test_zipped(self):
        files = DumpFile.get_last_of_type(DumpFile.TYPE_SQL, node=None)
        sql_dump_file = files[0]
        self.assertTrue(sql_dump_file.zipdumpfile_set.count())

    def init_db(self):
        files = DumpFile.get_last_of_type(DumpFile.TYPE_SQL, node=None)

        self.assertTrue(files)

        sql_dump_file = files[0]
        f = NamedTemporaryFile(delete=False)
        f.write(sql_dump_file.file.read())
        f.seek(0)
        f.close()
        proxy.initialize(peewee.SqliteDatabase(f.name))
        proxy.create_tables([Metadatos], safe=True)

    @classmethod
    def tearDownClass(cls):
        super(SQLTests, cls).tearDownClass()
        connections.get_connection().indices.delete(cls.index)
