# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import faker
from elasticsearch_dsl import Index
from django.test import TestCase
from django_datajsonar.tasks import read_datajson
from django_datajsonar.models import ReadDataJsonTask, Node, Field as datajsonar_Field

from series_tiempo_ar_api.apps.metadata.indexer.catalog_meta_indexer import CatalogMetadataIndexer
from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field
from series_tiempo_ar_api.apps.metadata.indexer.index import add_analyzer
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.apps.management import meta_keys
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')

fake = faker.Faker()

fake_index = Index(fake.word(), using=ElasticInstance.get())
add_analyzer(fake_index)


class IndexerTests(TestCase):

    class FakeField(Field):
        class Meta:
            index = fake_index._name

    def setUp(self):
        self.elastic = ElasticInstance.get()
        self.task = ReadDataJsonTask.objects.create()
        self.meta_task = IndexMetadataTask.objects.create()
        fake_index.doc_type(self.FakeField)
        fake_index.create()
        self.FakeField.init(using=self.elastic)

    def test_index(self):
        self._index(catalog_id='test_catalog', catalog_url='single_distribution.json')
        search = self.FakeField.search(
            using=self.elastic
        ).filter('term',
                 catalog_id='test_catalog')

        self.assertTrue(search.execute())

    def test_index_unavailable_fields(self):
        self._index(catalog_id='test_catalog', catalog_url='single_distribution.json', set_availables=False)
        search = self.FakeField.search(
            using=self.elastic
        ).filter('term',
                 catalog_id='test_catalog')

        self.assertFalse(search.execute())

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

        CatalogMetadataIndexer(node, self.meta_task, self.FakeField).index()
        self.elastic.indices.forcemerge()

    def tearDown(self):
        fake_index.delete()
