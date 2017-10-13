#! coding: utf-8
import os

from django.test import TestCase

from elastic_spike.apps.api.query.catalog_reader import Scraper

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class ScrapperTests(TestCase):

    def setUp(self):
        self.scrapper = Scraper()

    def test_scrapper(self):
        catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
        self.scrapper.run(catalog)

        self.assertTrue(len(self.scrapper.distributions))

    def test_remote_datajson(self):
        url = 'http://infra.datos.gob.ar/catalog/sspm/data.json'

        self.scrapper.run(url)

        self.assertGreaterEqual(len(self.scrapper.distributions), 400)
