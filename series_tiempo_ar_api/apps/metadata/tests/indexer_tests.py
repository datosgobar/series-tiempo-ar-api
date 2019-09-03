# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import faker
from elasticsearch_dsl import Index, Search
from elasticsearch_dsl.connections import connections
from django.test import TestCase
from django_datajsonar.tasks import read_datajson
from django_datajsonar.models import ReadDataJsonTask, Node, Field as datajsonar_Field, Catalog

from series_tiempo_ar_api.apps.metadata.indexer.catalog_meta_indexer import CatalogMetadataIndexer
from series_tiempo_ar_api.apps.metadata.indexer.index import add_analyzer
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from series_tiempo_ar_api.apps.management import meta_keys

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class IndexerTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(IndexerTests, cls).setUpClass()
        Catalog.objects.all().delete()
        fake = faker.Faker()

        cls.fake_index = Index(fake.pystr(max_chars=50).lower())
        add_analyzer(cls.fake_index)

    def setUp(self):
        self.task = ReadDataJsonTask.objects.create()
        self.meta_task = IndexMetadataTask.objects.create()

    def test_index(self):
        series_indexed = self._index(catalog_id='test_catalog',
                                     catalog_url='single_distribution.json')
        search = Search(
            index=self.fake_index._name,
        ).filter('term',
                 catalog_id='test_catalog')
        self.assertTrue(series_indexed)
        self.assertTrue(search.execute())

    def test_index_unavailable_fields(self):
        series_indexed = self._index(catalog_id='test_catalog',
                                     catalog_url='single_distribution.json',
                                     set_availables=False)

        self.assertFalse(series_indexed)

    def test_errored_fields(self):
        series_indexed = self._index(catalog_id='test_catalog',
                                     catalog_url='single_distribution.json',
                                     set_error=True)

        self.assertTrue(series_indexed)

    def test_non_present_fields(self):
        series_indexed = self._index(catalog_id='test_catalog',
                                     catalog_url='single_distribution.json',
                                     set_present=False)

        self.assertTrue(series_indexed)

    def test_multiple_catalogs(self):
        self._index(catalog_id='test_catalog',
                    catalog_url='single_distribution.json')

        self._index(catalog_id='other_catalog',
                    catalog_url='second_single_distribution.json')

        search = Search(
            index=self.fake_index._name,
        ).filter('term',
                 catalog_id='test_catalog')
        self.assertTrue(search.execute())

        other_search = Search(
            index=self.fake_index._name,
        ).filter('term',
                 catalog_id='other_catalog')
        self.assertTrue(other_search.execute())

    def test_index_no_theme_taxonomy(self):
        self._index(catalog_id='test_catalog',
                    catalog_url='no_theme_taxonomy.json')
        search = Search(
            index=self.fake_index._name,
        ).filter('term',
                 catalog_id='test_catalog')
        self.assertTrue(search.execute())

    def test_index_year_periodicity(self):
        self._index(catalog_id='test_catalog',
                    catalog_url='single_distribution.json',
                    periodicity='R/P1Y')
        search = Search(
            index=self.fake_index._name,
        ).filter('term', catalog_id='test_catalog').filter('term', periodicity_index=0)
        self.assertTrue(search.execute())

    def test_index_semester_periodicity(self):
        self._index(catalog_id='test_catalog',
                    catalog_url='semester_periodicity_distribution.json',
                    periodicity='R/P6M')
        search = Search(
            index=self.fake_index._name,
        ).filter('term', catalog_id='test_catalog').filter('term', periodicity_index=1)
        self.assertTrue(search.execute())

    def test_index_quarter_periodicity(self):
        self._index(catalog_id='test_catalog',
                    catalog_url='quarter_periodicity_distribution.json',
                    periodicity='R/P3M')
        search = Search(
            index=self.fake_index._name,
        ).filter('term', catalog_id='test_catalog').filter('term', periodicity_index=2)
        self.assertTrue(search.execute())

    def test_index_month_periodicity(self):
        self._index(catalog_id='test_catalog',
                    catalog_url='month_periodicity_distribution.json',
                    periodicity='R/P1M')
        search = Search(
            index=self.fake_index._name,
        ).filter('term', catalog_id='test_catalog').filter('term', periodicity_index=3)
        self.assertTrue(search.execute())

    def test_index_week_periodicity(self):
        self._index(catalog_id='test_catalog',
                    catalog_url='week_periodicity_distribution.json',
                    periodicity='R/P1W')
        search = Search(
            index=self.fake_index._name,
        ).filter('term', catalog_id='test_catalog').filter('term', periodicity_index=4)
        self.assertTrue(search.execute())

    def test_index_day_periodicity(self):
        self._index(catalog_id='test_catalog',
                    catalog_url='day_periodicity_distribution.json')
        search = Search(
            index=self.fake_index._name,
        ).filter('term', catalog_id='test_catalog').filter('term', periodicity_index=5)
        self.assertTrue(search.execute())

    def _index(self, catalog_id, catalog_url, periodicity='R/P1D', set_availables=True, set_error=False, set_present=True):
        node = Node.objects.create(
            catalog_id=catalog_id,
            catalog_url=os.path.join(SAMPLES_DIR, catalog_url),
            indexable=True,
        )

        read_datajson(self.task, whitelist=True, read_local=True)
        if set_availables:
            for field in datajsonar_Field.objects.all():
                field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')
                field.enhanced_meta.create(key=meta_keys.HITS_90_DAYS, value='0')
                field.enhanced_meta.create(key=meta_keys.PERIODICITY, value=periodicity)

        datajsonar_Field.objects.update(error=set_error, present=set_present)

        index_ok = CatalogMetadataIndexer(node, self.meta_task, self.fake_index._name).index()
        if index_ok:
            connections.get_connection().indices.forcemerge()
        return index_ok

    def tearDown(self):
        if self.fake_index.exists():
            self.fake_index.delete()
