# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import mock
from django.test import TestCase
from elasticsearch_dsl import Search
from pydatajson import DataJson

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field
from series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer import CatalogMetadataIndexer
from series_tiempo_ar_api.apps.metadata.queries.query import FieldSearchQuery
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from .utils import get_mock_search, MOCK_DATA

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
mock.patch.object = mock.patch.object  # Hack for pylint inspection


class QueryTests(TestCase):

    def test_no_querystring(self):
        query = FieldSearchQuery(args={})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_bad_limit(self):
        query = FieldSearchQuery(args={'limit': 'invalid'})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_bad_offset(self):
        query = FieldSearchQuery(args={'offset': 'invalid'})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_query_response_size(self):
        query = FieldSearchQuery(args={'q': 'aceite'})

        with mock.patch.object(Search, 'execute', return_value=get_mock_search()):
            result = query.execute()

        self.assertEqual(len(result['data']), result['count'])

    def test_response_params(self):
        limit = '10'
        offset = '15'
        query = FieldSearchQuery(args={'q': 'aceite',
                                       'limit': limit,
                                       'offset': offset})

        with mock.patch.object(Search, 'execute', return_value=get_mock_search()):
            result = query.execute()

        self.assertEqual(result['limit'], int(limit))
        self.assertEqual(result['offset'], int(offset))

    def test_add_filter(self):
        q = FieldSearchQuery(args={'units': 'unit_test'})
        search = q.add_filters(Search(), 'units', 'units').to_dict()

        # Esperado: un filter agregado
        filters = search['query']['bool']['filter']
        self.assertEqual(len(filters), 1)
        self.assertEqual(filters[0]['terms']['units'], ['unit_test'])

    def test_add_filter_no_param(self):
        q = FieldSearchQuery(args={})
        search = Search()
        prev_dict = search.to_dict()
        search = q.add_filters(search, 'units', 'units').to_dict()
        # Esperado: no se modifica la query si no hay parámetros
        self.assertEqual(prev_dict, search)

    def test_enhanced_meta(self):
        q = FieldSearchQuery(args={'q': 'a'})

        with mock.patch.object(Search, 'execute', return_value=get_mock_search()):
            result = q.execute()

        self.assertTrue(result['data'][0]['field']['periodicity'], MOCK_DATA['periodicity'])
        self.assertTrue(result['data'][0]['field']['start_date'], MOCK_DATA['start_date'])
        self.assertTrue(result['data'][0]['field']['end_date'], MOCK_DATA['end_date'])


class CatalogIndexerTests(TestCase):

    def setUp(self):
        self.task = IndexMetadataTask()
        # No mandar datos a la instancia de ES
        CatalogMetadataIndexer.init_index = mock.Mock()
        CatalogMetadataIndexer.index_actions = mock.Mock()

    def test_scraping(self):
        catalog = os.path.join(SAMPLES_DIR, 'single_distribution.json')
        datajson = DataJson(catalog)
        result = CatalogMetadataIndexer(datajson, 'test_node', self.task).scrap_datajson()

        self.assertEqual(len(result), len(datajson.get_fields()) - 1)

    def test_scraping_result(self):
        catalog = os.path.join(SAMPLES_DIR, 'single_distribution.json')
        datajson = DataJson(catalog)
        result = CatalogMetadataIndexer(datajson, 'test_node', self.task).scrap_datajson()

        mapping = Field._doc_type.mapping.properties.properties.to_dict()
        mapping_fields = mapping.keys()

        # Me aseguro que los resultados sean legibles por el indexer de ES
        for field in result:
            for key in field['_source'].keys():
                self.assertIn(key, mapping_fields)

            self.assertEqual(field['_index'], constants.FIELDS_INDEX)
