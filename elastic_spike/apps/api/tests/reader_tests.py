#! coding: utf-8
import os

import time
from django.test import TestCase
from series_tiempo_ar.search import get_time_series_distributions
from elasticsearch_dsl import Search

from elastic_spike.apps.api.models import Distribution
from elastic_spike.apps.api.query.elastic import ElasticInstance
from elastic_spike.apps.api.query.catalog_reader import Scraper, Indexer, \
    DatabaseLoader

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class ScrapperTests(TestCase):

    def setUp(self):
        self.scrapper = Scraper(read_local=True)

    def test_scrapper(self):
        catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
        self.scrapper.run(catalog)

        self.assertTrue(len(self.scrapper.distributions))


class IndexerTests(TestCase):
    test_index = "test_indicators"

    def setUp(self):
        catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
        distributions = get_time_series_distributions(catalog)
        DatabaseLoader(read_local=True).run(catalog, distributions)
        self.indexer = Indexer(index=self.test_index)

    def test_init_dataframe_columns(self):
        distribution = Distribution.objects.get(identifier="212.1")
        fields = distribution.field_set.all()
        fields = {field.title: field.series_id for field in fields}
        df = Indexer.init_df(distribution, fields)

        for field in fields:
            self.assertTrue(field in df.columns)

    def test_indexing(self):
        self.indexer.run()

        results = Search(using=ElasticInstance.get(),
                         index=self.test_index).execute()
        self.assertTrue(len(results))

    @classmethod
    def tearDownClass(cls):
        ElasticInstance.get().indices.delete(index=cls.test_index)
