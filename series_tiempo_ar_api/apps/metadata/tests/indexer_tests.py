#! coding: utf-8
import os

from django.test import TestCase

from series_tiempo_ar_api.apps.management.models import Node
from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field
from series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer import MetadataIndexer
from series_tiempo_ar_api.apps.metadata.tests.tests import SAMPLES_DIR
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance

from faker import Faker

fake = Faker()


class IndexerTests(TestCase):
    class FakeField(Field):
        class Meta:
            index = fake.word()

    def setUp(self):
        self.elastic = ElasticInstance.get()

    def test_index_two_nodes(self):
        Node(catalog_id='first_catalog',
             catalog_url=os.path.join(SAMPLES_DIR, 'single_distribution.json'),
             indexable=True).save()
        Node(catalog_id='second_catalog',
             catalog_url=os.path.join(SAMPLES_DIR, 'second_single_distribution.json'),
             indexable=True).save()

        MetadataIndexer(doc_type=self.FakeField).run()

        first_catalog_fields = self.FakeField.search(using=ElasticInstance.get())\
            .filter('term', catalog_id='first_catalog')\
            .execute()

        second_catalog_fields = self.FakeField.search(using=ElasticInstance.get())\
            .filter('term', catalog_id='second_catalog')\
            .execute()

        self.assertTrue(first_catalog_fields)
        self.assertTrue(second_catalog_fields)

    def tearDown(self):
        self.elastic.indices.delete(self.FakeField._doc_type.index)
