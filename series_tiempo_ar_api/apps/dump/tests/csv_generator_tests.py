#! coding: utf-8
import io
import json
import os
import csv
import zipfile

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django_datajsonar.models import Field, Node, Catalog
from elasticsearch_dsl.connections import connections

from faker import Faker

from series_tiempo_ar_api.apps.dump.constants import VALUES_HEADER
from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.dump.generator.generator import DumpGenerator
from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask, DumpFile, ZipDumpFile
from series_tiempo_ar_api.utils.utils import index_catalog, read_file_as_csv

samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class CSVTest(TestCase):
    index = 'csv_dump_test_index'
    # noinspection PyUnresolvedReferences
    directory = os.path.join(settings.MEDIA_ROOT, 'test_dump')

    @classmethod
    def setUpClass(cls):
        super(CSVTest, cls).setUpClass()
        cls.catalog_id = 'csv_dump_test_catalog'
        path = os.path.join(samples_dir, 'distribution_daily_periodicity.json')
        index_catalog(cls.catalog_id, path, cls.index)
        cls.task = GenerateDumpTask()
        cls.task.save()
        gen = DumpGenerator(cls.task)
        gen.generate()

    def test_invalid_catalog(self):
        task = GenerateDumpTask()
        task.save()

        gen = DumpGenerator(task, "no_catalog")
        gen.generate()
        task.refresh_from_db()

        self.assertFalse(DumpFile.objects.filter(file_type=DumpFile.TYPE_CSV, task=task))

    def test_values_dump(self):
        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_VALUES).file
        reader = read_file_as_csv(file)
        next(reader)  # skip header
        row = next(reader)
        self.assertEqual(row[0], self.catalog_id)
        self.assertEqual(row[6], 'R/P1D')

    def test_values_length(self):
        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_VALUES).file
        reader = read_file_as_csv(file)
        header = next(reader)
        self.assertEqual(len(header), 7)

    def test_entity_identifiers(self):
        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_VALUES).file
        reader = read_file_as_csv(file)
        next(reader)

        row = next(reader)

        field_id = row[3]
        field = Field.objects.get(identifier=field_id)

        self.assertEqual(self.catalog_id, row[0])
        self.assertEqual(field.distribution.identifier, row[2])
        self.assertEqual(field.distribution.dataset.identifier, row[1])
        self.assertEqual(row[6], field.distribution.enhanced_meta.get(key=meta_keys.PERIODICITY).value)

    def test_full_csv_zipped(self):
        dump_file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_FULL,
                                               file_type=DumpFile.TYPE_CSV)
        zip_file = ZipDumpFile.objects.get(dump_file=dump_file).file
        csv_zipped = zipfile.ZipFile(zip_file)

        full_csv = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_FULL,
                                              file_type=DumpFile.TYPE_CSV)
        # Necesario para abrir archivos zippeados en modo texto (no bytes)
        src_file = io.TextIOWrapper(csv_zipped.open(full_csv.get_file_name()),
                                    encoding='utf8',
                                    newline='')
        reader = csv.reader(src_file)

        header = next(reader)

        self.assertEqual(len(header), 15)

    def test_values_csv_zipped(self):
        dump_file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_VALUES,
                                               file_type=DumpFile.TYPE_CSV)
        zip_file = ZipDumpFile.objects.get(dump_file=dump_file).file
        csv_zipped = zipfile.ZipFile(zip_file)

        # Necesario para abrir archivos zippeados en modo texto (no bytes)
        src_file = io.TextIOWrapper(csv_zipped.open(dump_file.get_file_name()),
                                    encoding='utf8',
                                    newline='')
        reader = csv.reader(src_file)

        header = next(reader)

        self.assertEqual(len(header), len(VALUES_HEADER))

    def test_full_csv_identifier_fields(self):
        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_FULL,
                                          file_type=DumpFile.TYPE_CSV).file
        reader = read_file_as_csv(file)
        next(reader)  # Header

        row = next(reader)

        field = Field.objects.get(identifier=row[3])
        self.assertEqual(row[0], self.catalog_id)
        self.assertEqual(row[1], field.distribution.dataset.identifier)
        self.assertEqual(row[2], field.distribution.identifier)
        self.assertEqual(row[5], field.distribution.enhanced_meta.get(key=meta_keys.PERIODICITY).value)

    def test_full_csv_metadata_fields(self):
        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_FULL,
                                          file_type=DumpFile.TYPE_CSV).file
        reader = read_file_as_csv(file)
        next(reader)  # Header

        row = next(reader)

        field = Field.objects.get(identifier=row[3])

        field_meta = json.loads(field.metadata)
        distribution_meta = json.loads(field.distribution.metadata)
        self.assertEqual(row[7], field.title)
        self.assertEqual(row[8], field_meta['units'])
        self.assertEqual(row[9], field_meta['description'])
        self.assertEqual(row[10], distribution_meta['description'])

    def test_full_csv_dataset_metadata_fields(self):
        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_FULL,
                                          file_type=DumpFile.TYPE_CSV).file
        reader = read_file_as_csv(file)
        next(reader)  # Header

        row = next(reader)

        field = Field.objects.get(identifier=row[3])

        dataset_meta = json.loads(field.distribution.dataset.metadata)
        self.assertEqual(row[12], dataset_meta['publisher']['name'])
        self.assertEqual(row[13], dataset_meta['source'])
        self.assertEqual(row[14], field.distribution.dataset.title)

    def test_full_csv_dataset_theme_field(self):
        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_FULL,
                                          file_type=DumpFile.TYPE_CSV).file
        reader = read_file_as_csv(file)
        next(reader)  # Header
        row = next(reader)

        field = Field.objects.get(identifier=row[3])

        dataset_meta = json.loads(field.distribution.dataset.metadata)

        themes = json.loads(Node.objects.get(catalog_id=self.catalog_id).catalog)['themeTaxonomy']

        theme_label = ''
        for theme in themes:
            if theme['id'] == dataset_meta['theme'][0]:
                theme_label = theme['label']
                break

        self.assertEqual(theme_label, row[11])

    def test_metadata_csv(self):
        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_METADATA).file
        reader = read_file_as_csv(file)
        next(reader)

        self.assertEqual(len(list(reader)), 3)  # Un row por serie

    def test_sources_csv(self):
        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_SOURCES).file
        reader = read_file_as_csv(file)
        next(reader)  # Header

        self.assertEqual(len(list(reader)), 1)  # Un row por fuente

    def test_sources_csv_columns(self):
        dataset = Field.objects.first().distribution.dataset
        meta = json.loads(dataset.metadata)

        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_SOURCES).file
        reader = read_file_as_csv(file)
        next(reader)  # Header

        row = next(reader)
        series = Field.objects.exclude(title='indice_tiempo')
        self.assertEqual(row[0], meta['source'])  # nombre de la fuente
        self.assertEqual(int(row[1]), 3)  # Cantidad de series
        self.assertEqual(int(row[2]), sum([int(meta_keys.get(x, meta_keys.INDEX_SIZE))
                                           for x in series]))
        self.assertEqual(row[3], min(meta_keys.get(x, meta_keys.INDEX_START) for x in series))
        self.assertEqual(row[4], max(meta_keys.get(x, meta_keys.INDEX_END) for x in series))

    def test_leading_nulls_distribution(self):
        path = os.path.join(samples_dir, 'leading_nulls_distribution.json')
        index_catalog('leading_null', path, self.index)
        self.task = GenerateDumpTask()
        self.task.save()
        gen = DumpGenerator(self.task, 'leading_null')
        gen.generate()

        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_FULL,
                                          file_type=DumpFile.TYPE_CSV,
                                          node__catalog_id='leading_null').file
        reader = read_file_as_csv(file)

        next(reader)  # Header!!!!
        self.assertEqual(len(list(reader)), 1)  # Un único row, para un único valor del CSV

    def test_metadata_csv_hits(self):
        file = self.task.dumpfile_set.get(file_name=DumpFile.FILENAME_METADATA,
                                          file_type=DumpFile.TYPE_CSV).file
        reader = read_file_as_csv(file)
        next(reader)  # Header

        row = next(reader)

        field = Field.objects.get(identifier=row[3])
        self.assertEqual(row[25], meta_keys.get(field, meta_keys.HITS_TOTAL))
        self.assertEqual(row[26], meta_keys.get(field, meta_keys.HITS_30_DAYS))
        self.assertEqual(row[27], meta_keys.get(field, meta_keys.HITS_90_DAYS))
        self.assertEqual(row[28], meta_keys.get(field, meta_keys.HITS_180_DAYS))

    @classmethod
    def tearDownClass(cls):
        super(CSVTest, cls).tearDownClass()
        elastic = connections.get_connection()
        elastic.indices.delete(cls.index)
        Node.objects.all().delete()


class CSVDumpCommandTests(TestCase):

    def setUp(self):
        fake = Faker()
        self.index = fake.word()
        GenerateDumpTask.objects.all().delete()
        DumpFile.objects.all().delete()

        path = os.path.join(samples_dir, 'distribution_daily_periodicity.json')
        index_catalog('catalog_one', path, index=self.index)

        path = os.path.join(samples_dir, 'leading_nulls_distribution.json')
        index_catalog('catalog_two', path, index=self.index)

    def test_command_creates_model(self):
        call_command('generate_dump')
        self.assertEqual(GenerateDumpTask.objects.count(), 1)

        task = GenerateDumpTask.objects.first()
        self.assertTrue(task.dumpfile_set.count(), task.logs)

    def test_catalog_dumps(self):
        call_command('generate_dump')
        # Tres dumps generados, 1 por cada catálogo y uno global
        self.assertTrue(DumpFile.objects.get(file_name=DumpFile.FILENAME_VALUES, node__catalog_id='catalog_one'))
        self.assertTrue(DumpFile.objects.get(file_name=DumpFile.FILENAME_VALUES, node__catalog_id='catalog_two'))
        self.assertTrue(DumpFile.objects.get(file_name=DumpFile.FILENAME_VALUES, node=None))

    def test_zipped_catalogs(self):
        call_command('generate_dump')
        # Tres dumps generados, 1 por cada catálogo y uno global
        self.assertTrue(DumpFile.objects.get(file_name=DumpFile.FILENAME_FULL,
                                             file_type=DumpFile.TYPE_CSV,
                                             node=None).zipdumpfile_set.first())
        self.assertTrue(DumpFile.objects.get(file_name=DumpFile.FILENAME_FULL,
                                             file_type=DumpFile.TYPE_CSV,
                                             node__catalog_id='catalog_one').zipdumpfile_set.first())
        self.assertTrue(DumpFile.objects.get(file_name=DumpFile.FILENAME_FULL,
                                             file_type=DumpFile.TYPE_CSV,
                                             node__catalog_id='catalog_two').zipdumpfile_set.first())

    def tearDown(self):
        elastic = connections.get_connection()
        elastic.indices.delete(self.index)
        Catalog.objects.all().delete()
        DumpFile.objects.all().delete()
        Node.objects.all().delete()
