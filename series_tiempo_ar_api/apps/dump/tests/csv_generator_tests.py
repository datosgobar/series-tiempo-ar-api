#! coding: utf-8
import io
import os
import csv
import shutil
import zipfile

from django.test import TestCase
from django_datajsonar.models import Field

from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.apps.dump.csv import CSVDumpGenerator
from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.utils import index_catalog

samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class CSVTest(TestCase):
    index = 'csv_dump_test_index'
    # noinspection PyUnresolvedReferences
    directory = os.path.join(samples_dir, 'output')

    @classmethod
    def setUpClass(cls):
        super(CSVTest, cls).setUpClass()
        cls.catalog_id = 'csv_dump_test_catalog'
        path = os.path.join(samples_dir, 'distribution_daily_periodicity.json')
        os.mkdir(cls.directory)
        index_catalog(cls.catalog_id, path, cls.index)
        gen = CSVDumpGenerator(index=cls.index, output_directory=cls.directory)
        gen.generate()

    def test_values_dump(self):
        reader = csv.reader(open(os.path.join(self.directory, constants.VALUES_CSV)))
        next(reader)  # skip header
        row = next(reader)
        self.assertEqual(row[0], self.catalog_id)
        self.assertEqual(row[6], 'R/P1D')

    def test_values_length(self):
        reader = csv.reader(open(os.path.join(self.directory, constants.VALUES_CSV)))
        header = next(reader)
        self.assertEqual(len(header), 7)

    def test_entity_identifiers(self):
        reader = csv.reader(open(os.path.join(self.directory, constants.VALUES_CSV)))
        next(reader)

        row = next(reader)

        field_id = row[3]
        field = Field.objects.get(identifier=field_id)

        self.assertEqual(field.distribution.identifier, row[2])
        self.assertEqual(field.distribution.dataset.identifier, row[1])

    def test_full_csv_zipped(self):
        csv_zipped = zipfile.ZipFile(os.path.join(self.directory, constants.FULL_CSV_ZIPPED))

        # Necesario para abrir archivos zippeados en modo texto (no bytes)
        src_file = io.TextIOWrapper(csv_zipped.open(constants.FULL_CSV),
                                    encoding='utf8',
                                    newline='')
        reader = csv.reader(src_file)

        header = next(reader)

        self.assertEqual(len(header), 15)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.directory)
        ElasticInstance.get().indices.delete(cls.index)
