#! coding: utf8

from django.test import TestCase
from faker import Faker

from elasticsearch_dsl.connections import connections
from series_tiempo_ar_api.apps.metadata.indexer.index import get_fields_meta_index
from series_tiempo_ar_api.apps.metadata.models import Synonym
from series_tiempo_ar_api.apps.metadata import constants


class IndexTests(TestCase):
    index_name = Faker().pystr().lower()

    def test_no_synonyms_has_no_filter(self):
        index = get_fields_meta_index(self.index_name).to_dict()

        analyzer = index['settings']['analysis']['analyzer'][constants.ANALYZER]
        self.assertNotIn(constants.SYNONYM_FILTER, analyzer['filter'])

    def test_add_synonym(self):
        terms = 'test,terms'
        Synonym.objects.create(terms=terms)
        index = get_fields_meta_index(self.index_name).to_dict()
        filters = index['settings']['analysis']['filter'][constants.SYNONYM_FILTER]
        self.assertIn(terms, filters['synonyms'])

    def test_add_many_synonyms(self):
        terms = ["one,two", "three,four", "five,six"]
        for term in terms:
            Synonym.objects.create(terms=term)

        index = get_fields_meta_index(self.index_name).to_dict()
        filters = index['settings']['analysis']['filter'][constants.SYNONYM_FILTER]

        self.assertEqual(len(filters['synonyms']), 3)
        self.assertEqual(set(filters['synonyms']), set(terms))

    def tearDown(self) -> None:
        elastic = connections.get_connection()
        if elastic.indices.exists(self.index_name):
            elastic.indices.delete(self.index_name)
