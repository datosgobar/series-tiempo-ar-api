import os
from unittest import mock

from django.test import TestCase
from django_datajsonar.models import Distribution, Catalog, Node, ReadDataJsonTask
from django_datajsonar.tasks import read_datajson

from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class DistributionIndexerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Catalog.objects.all().delete()

    def test_index_series_no_identifier(self):
        catalog = os.path.join(SAMPLES_DIR, 'series_metadata_no_identifier.json')
        self._index_catalog(catalog)

        distribution = Distribution.objects.first()

        actions = DistributionIndexer('some_index').generate_es_actions(distribution)

        self.assertFalse(actions)

    def _index_catalog(self, catalog_path):
        self.read_data(catalog_path)
        with mock.patch('series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer.parallel_bulk'):
            distributions = Distribution.objects.all()

            for distribution in distributions:
                DistributionIndexer('some_index').reindex(distribution)

    def read_data(self, catalog_path):
        Node.objects.create(catalog_id='test_catalog', catalog_url=catalog_path, indexable=True)
        task = ReadDataJsonTask.objects.create()

        read_datajson(task, whitelist=True)
