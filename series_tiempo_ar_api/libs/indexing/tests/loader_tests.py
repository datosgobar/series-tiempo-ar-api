#! coding: utf-8
import json
import os

from django.conf import settings
from django.test import TestCase
from pydatajson import DataJson
from nose.tools import raises
from series_tiempo_ar.search import get_time_series_distributions

from series_tiempo_ar_api.apps.api.models import Catalog, Dataset, Distribution, Field
from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask, Node
from series_tiempo_ar_api.libs.indexing.database_loader import DatabaseLoader, FieldRepetitionError
from series_tiempo_ar_api.libs.indexing.tests.reader_tests import SAMPLES_DIR, CATALOG_ID

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class DatabaseLoaderTests(TestCase):

    catalog_id = 'test_catalog'

    def setUp(self):
        self.task = ReadDataJsonTask()
        self.task.save()
        self.node = Node(catalog_id=self.catalog_id,
                         catalog_url=os.path.join(dir_path, 'full_ts_data.json'),
                         indexable=True)
        self.node.save()

        self.init_datasets(self.node)
        self.loader = DatabaseLoader(self.task, read_local=True, default_whitelist=True)

    @staticmethod
    def init_datasets(node, whitelist=True):
        catalog_model, created = Catalog.objects.get_or_create(identifier=node.catalog_id)
        catalog = DataJson(json.loads(node.catalog))
        if created:
            catalog_model.title = catalog['title'],
            catalog_model.metadata = '{}'
            catalog_model.save()
        for dataset in catalog.get_datasets(only_time_series=True):
            dataset_model, created = Dataset.objects.get_or_create(
                catalog=catalog_model,
                identifier=dataset['identifier']
            )
            if created:
                dataset_model.metadata = '{}'
                dataset_model.indexable = whitelist
                dataset_model.save()

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
        Catalog.objects.all().delete()  # Fuerza a recrear los modelos

        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        distributions = get_time_series_distributions(catalog)
        self.node.catalog = json.dumps(catalog)
        self.init_datasets(self.node, whitelist=False)
        loader = DatabaseLoader(self.task, read_local=True, default_whitelist=False)
        loader.run(distributions[0], catalog, self.catalog_id)
        dataset = Catalog.objects.get(identifier=CATALOG_ID).dataset_set

        self.assertEqual(dataset.count(), 1)
        self.assertFalse(dataset.first().indexable)

    def test_change_series_distribution(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        distributions = get_time_series_distributions(catalog)

        self.loader.run(distributions[0], catalog, self.catalog_id)

        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data_changed_distribution.json'))
        self.node.catalog = json.dumps(catalog)
        self.init_datasets(self.node)
        distributions = get_time_series_distributions(catalog)
        loader = DatabaseLoader(self.task, read_local=True, default_whitelist=True)
        loader.run(distributions[0], catalog, self.catalog_id)

        # Valores obtenidos del .json fuente
        self.assertEqual(Field.objects.get(series_id="212.1_PSCIOS_IOS_0_0_25").distribution,
                         Distribution.objects.get(identifier="300.1"))

    @raises(FieldRepetitionError)
    def test_change_series_distributions_different_catalog(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        distributions = get_time_series_distributions(catalog)

        self.loader.run(distributions[0], catalog, self.catalog_id)

        other_catalog_id = 'other_catalog_id'
        node = Node(catalog_id=other_catalog_id,
                    catalog_url=os.path.join(SAMPLES_DIR, 'full_ts_data_changed_distribution.json'),
                    indexable=True)
        node.save()
        loader = DatabaseLoader(self.task, read_local=True, default_whitelist=True)

        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data_changed_distribution.json'))
        distributions = get_time_series_distributions(catalog)
        self.node.catalog = json.dumps(catalog)
        self.node.catalog_id = 'other_catalog_id'
        self.init_datasets(self.node)
        loader.run(distributions[0], catalog, 'other_catalog_id')
