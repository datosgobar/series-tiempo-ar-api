import os

import faker
import pandas as pd
from django.test import TestCase
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.dump.generator import constants
from series_tiempo_ar_api.apps.dump.generator.dta import DtaGenerator
from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask, DumpFile
from series_tiempo_ar_api.apps.dump.tasks import enqueue_write_csv_task
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.utils.utils import index_catalog

samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')

fake = faker.Faker()


class DtaGeneratorTests(TestCase):
    index = fake.pystr(max_chars=50).lower()

    @classmethod
    def setUpClass(cls):
        index_catalog('test_catalog', os.path.join(samples_dir, 'distribution_daily_periodicity.json'), cls.index)
        enqueue_write_csv_task()
        super(DtaGeneratorTests, cls).setUpClass()

    def test_generate_dta_no_csv_loaded(self):
        node = Node.objects.create(catalog_id="empty_catalog", catalog_url="test.com", indexable=True)
        task = GenerateDumpTask.objects.create()
        DtaGenerator(task.id).generate()
        self.assertFalse(DumpFile.objects.filter(node=node, file_type=DumpFile.TYPE_DTA))

    def test_generate_dta(self):
        task = GenerateDumpTask.objects.create()
        DtaGenerator(task.id).generate()

        csv = DumpFile.objects.get(file_type=DumpFile.TYPE_CSV,
                                   file_name=DumpFile.FILENAME_VALUES,
                                   node=None).file

        rows_len = len(pd.read_csv(csv))

        stata = DumpFile.objects.get(file_type=DumpFile.TYPE_DTA,
                                     file_name=DumpFile.FILENAME_VALUES,
                                     node=None).file

        self.assertGreater(rows_len, 0)
        self.assertEqual(rows_len, len(pd.read_stata(stata)))

    def test_values_dta_columns(self):
        task = GenerateDumpTask.objects.create()
        DtaGenerator(task.id).generate()
        stata = DumpFile.objects.get(file_type=DumpFile.TYPE_DTA,
                                     file_name=DumpFile.FILENAME_VALUES,
                                     node=None).file
        df = pd.read_stata(stata)
        self.assertListEqual(list(df.columns), constants.STATA_VALUES_COLS)

    @classmethod
    def tearDownClass(cls):
        ElasticInstance.get().indices.delete(cls.index)
        super(DtaGeneratorTests, cls).tearDownClass()
