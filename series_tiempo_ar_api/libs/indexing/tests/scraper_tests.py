#! coding: utf-8
import os

from pydatajson import DataJson
from django.test import TestCase

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.libs.indexing.scraping import Scraper
from series_tiempo_ar_api.libs.indexing.tests.reader_tests import SAMPLES_DIR


class ScrapperTests(TestCase):
    def setUp(self):
        self.task = ReadDataJsonTask()
        self.task.save()
        self.scrapper = Scraper(self.task, read_local=True)

    def test_scrapper(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        result = self.scrapper.run(catalog.get_distributions(only_time_series=True)[0], catalog)

        self.assertTrue(result)

    def test_missing_metadata_field(self):
        """No importa que un field no esté en metadatos, se scrapea
        igual, para obtener todas las series posibles
        """

        catalog = DataJson(os.path.join(SAMPLES_DIR, 'missing_field.json'))
        result = self.scrapper.run(catalog.get_distributions(only_time_series=True)[0], catalog)
        self.assertTrue(result)

    def test_missing_dataframe_column(self):
        """Si falta una columna indicada por los metadatos, no se
        scrapea la distribución
        """

        catalog = DataJson(os.path.join(
            SAMPLES_DIR, 'distribution_missing_column.json'
        ))
        result = self.scrapper.run(catalog.get_distributions(only_time_series=True)[0], catalog)
        self.assertFalse(result)
