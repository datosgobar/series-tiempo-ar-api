# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import faker
from elasticsearch_dsl import Index, Search
from django.test import TestCase
from django_datajsonar.tasks import read_datajson
from django_datajsonar.models import ReadDataJsonTask, Node, Field as datajsonar_Field

from series_tiempo_ar_api.apps.metadata.indexer.catalog_meta_indexer import CatalogMetadataIndexer
from series_tiempo_ar_api.apps.metadata.indexer.index import add_analyzer
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.apps.management import meta_keys
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')

fake = faker.Faker()

fake_index = Index(fake.pystr(max_chars=50).lower(), using=ElasticInstance.get())
add_analyzer(fake_index)


class IndexerTests(TestCase):

    def setUp(self):
        self.elastic = ElasticInstance.get()
        self.task = ReadDataJsonTask.objects.create()
        self.meta_task = IndexMetadataTask.objects.create()

    def test_index(self):
        index_ok = self._index(catalog_id='test_catalog', catalog_url='single_distribution.json')
        search = Search(
            index=fake_index._name,
            using=self.elastic
        ).filter('term',
                 catalog_id='test_catalog')
        self.assertTrue(index_ok)
        self.assertTrue(search.execute())

    def test_index_unavailable_fields(self):
        index_ok = self._index(catalog_id='test_catalog',
                               catalog_url='single_distribution.json',
                               set_availables=False)

        self.assertFalse(index_ok)

    def test_multiple_catalogs(self):
        self._index(catalog_id='test_catalog',
                               catalog_url='single_distribution.json')

        self._index(catalog_id='other_catalog',
                    catalog_url='second_single_distribution.json')

        search = Search(
            index=fake_index._name,
            using=self.elastic
        ).filter('term',
                 catalog_id='test_catalog')
        self.assertTrue(search.execute())

        other_search = Search(
            index=fake_index._name,
            using=self.elastic
        ).filter('term',
                 catalog_id='other_catalog')
        self.assertTrue(other_search.execute())

    def _index(self, catalog_id, catalog_url, set_availables=True):
        node = Node.objects.create(
            catalog_id=catalog_id,
            catalog_url=os.path.join(SAMPLES_DIR, catalog_url),
            indexable=True,
        )

        read_datajson(self.task, whitelist=True, read_local=True)
        if set_availables:
            for field in datajsonar_Field.objects.all():
                field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')

        index_ok = CatalogMetadataIndexer(node, self.meta_task, fake_index._name).index()
        if index_ok:
            self.elastic.indices.forcemerge()
        return index_ok

    def tearDown(self):
        if fake_index.exists():
            fake_index.delete()
