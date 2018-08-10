#! coding: utf8

from django.test import TestCase
from series_tiempo_ar_api.apps.metadata.indexer.index import get_fields_meta_index
from series_tiempo_ar_api.apps.metadata.models import Synonym
from series_tiempo_ar_api.apps.metadata import constants


class IndexTests(TestCase):

    def test_no_synonyms_has_no_filter(self):
        index = get_fields_meta_index().to_dict()

        analyzer = index['settings']['analysis']['analyzer'][constants.ANALYZER]
        self.assertNotIn(constants.SYNONYM_FILTER, analyzer['filter'])

    def test_add_synonym(self):
        terms = 'test,terms'
        Synonym.objects.create(terms=terms)
        index = get_fields_meta_index().to_dict()
        filters = index['settings']['analysis']['filter'][constants.SYNONYM_FILTER]
        self.assertIn(terms, filters['synonyms'])

    def test_add_many_synonyms(self):
        Synonym.objects.create(terms="one,two")
        Synonym.objects.create(terms="three,four")
        Synonym.objects.create(terms="five,six")

        index = get_fields_meta_index().to_dict()
        filters = index['settings']['analysis']['filter'][constants.SYNONYM_FILTER]

        self.assertEqual(len(filters['synonyms']), 3)
        self.assertEqual(set(filters['synonyms']), set(Synonym.get_synonyms_list()))
