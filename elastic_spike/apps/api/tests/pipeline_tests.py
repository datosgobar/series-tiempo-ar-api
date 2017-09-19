#! coding: utf-8
from django.test import TestCase

from elastic_spike.apps.api.pipeline import NameAndRepMode
from elastic_spike.apps.api.query import Query


class NameAndRepModeTest(TestCase):
    """Testea el comando que se encarga del parámetro 'ids' de la 
    query: el parseo de IDs de series y modos de representación de las
    mismas.
    """
    single_series = 'random-0'
    single_series_rep_mode = 'random-0:percent_change'

    def setUp(self):
        self.cmd = NameAndRepMode()
        self.query = Query()

    def test_invalid_series(self):
        invalid_series = 'invalid'
        self.cmd.run(self.query, {'ids': invalid_series})
        self.assertTrue(self.cmd.errors)

    def test_valid_series(self):
        self.cmd.run(self.query, {'ids': self.single_series})
        self.assertFalse(self.cmd.errors)

