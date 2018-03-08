#! coding: utf-8
import json
import os

from django.conf import settings
from django.test import TestCase
from pydatajson import DataJson
from series_tiempo_ar.search import get_time_series_distributions

from series_tiempo_ar_api.apps.api.models import Catalog, Dataset, Distribution
from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask, Node
from series_tiempo_ar_api.libs.indexing.database_loader import DatabaseLoader
from series_tiempo_ar_api.libs.indexing.tests.reader_tests import SAMPLES_DIR, CATALOG_ID

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class DatabaseLoaderTests(TestCase):

    catalog_id = 'test_catalog'

    def setUp(self):
        self.task = ReadDataJsonTask()
        self.task.save()
        Node(catalog_id=self.catalog_id,
             catalog_url=os.path.join(dir_path, 'full_ts_data.json'),
             indexable=True).save()
        self.loader = DatabaseLoader(self.task, read_local=True, default_whitelist=True)

    def tearDown(self):
        Catalog.objects.filter(identifier=self.catalog_id).delete()

    def test_blacklisted_catalog_meta(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        distributions = get_time_series_distributions(catalog)

        self.loader.run(distributions[0], catalog, self.catalog_id)
        meta = Catalog.objects.first().metadata
        meta = json.loads(meta)
        for field in settings.CATALOG_BLACKLIST:
            self.assertTrue(field not in meta)

    def test_blacklisted_dataset_meta(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        distributions = get_time_series_distributions(catalog)

        self.loader.run(distributions[0], catalog, self.catalog_id)

        meta = Dataset.objects.first().metadata
        meta = json.loads(meta)
        for field in settings.DATASET_BLACKLIST:
            self.assertTrue(field not in meta)

    def test_blacklisted_distrib_meta(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        distributions = get_time_series_distributions(catalog)

        self.loader.run(distributions[0], catalog, self.catalog_id)
        distribution = Distribution.objects.first()
        meta = distribution.metadata
        meta = json.loads(meta)
        for field in settings.DISTRIBUTION_BLACKLIST:
            self.assertTrue(field not in meta)

    def test_blacklisted_field_meta(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        distributions = get_time_series_distributions(catalog)

        self.loader.run(distributions[0], catalog, self.catalog_id)

        distribution = Distribution.objects.first()
        for field_model in distribution.field_set.all():
            for field in settings.FIELD_BLACKLIST:
                self.assertTrue(field not in field_model.metadata)

    def test_datasets_loaded_are_not_indexable(self):

        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        distributions = get_time_series_distributions(catalog)
        loader = DatabaseLoader(self.task, read_local=True, default_whitelist=False)
        loader.run(distributions[0], catalog, self.catalog_id)
        dataset = Catalog.objects.get(identifier=CATALOG_ID).dataset_set

        self.assertEqual(dataset.count(), 1)
        self.assertFalse(dataset.first().indexable)
