#! coding: utf-8
import os

from django.test import TestCase
from ..catalog_reader import Scrapper

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class ScrapperTests(TestCase):

    def setUp(self):
        self.scrapper = Scrapper()

    def test_scrapper(self):
        catalog = os.path.join(SAMPLES_DIR, 'full_data.json')
        self.scrapper.run(catalog)

        self.assertTrue(len(self.scrapper.distributions))

