# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import mock
from django.test import TestCase
from elasticsearch_dsl import Search

from series_tiempo_ar_api.apps.metadata.models import CatalogAlias
from series_tiempo_ar_api.apps.metadata.queries.query import FieldSearchQuery
from .utils import get_mock_search

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
mock.patch.object = mock.patch.object  # Hack for pylint inspection


class QueryTests(TestCase):

    def test_no_querystring_is_valid(self):
        query = FieldSearchQuery(args={})

        with mock.patch.object(Search, 'execute', return_value=get_mock_search()):
            result = query.execute()

        self.assertFalse(result.get('errors'))

    def test_bad_limit(self):
        query = FieldSearchQuery(args={'limit': 'invalid'})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_bad_offset(self):
        query = FieldSearchQuery(args={'https://github.com/datosgobar/series-tiempo-ar-api/issues/318': 'invalid'})

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

        mock_search = get_mock_search()
        with mock.patch.object(Search, 'execute', return_value=get_mock_search()):
            result = q.execute()

        self.assertTrue(result['data'][0]['field']['periodicity'], mock_search.periodicity)
        self.assertTrue(result['data'][0]['field']['start_date'], mock_search.start_date)
        self.assertTrue(result['data'][0]['field']['end_date'], mock_search.end_date)

    def test_catalog_id_filter_with_alias(self):
        alias = CatalogAlias.objects.create(alias='alias_id')
        alias.nodes.create(catalog_id='catalog_1', catalog_url='http://example.com/1', indexable=True)
        alias.nodes.create(catalog_id='catalog_2', catalog_url='http://example.com/2', indexable=True)
        q = FieldSearchQuery(args={'catalog_id': 'alias_id'})

        search = Search()
        filtered_search = q.add_filters(search, 'catalog_id', 'catalog_id')

        filtered_catalogs = filtered_search.to_dict()['query']['bool']['filter'][0]['terms']['catalog_id']
        self.assertEqual(set(filtered_catalogs), {'catalog_1', 'catalog_2'})
