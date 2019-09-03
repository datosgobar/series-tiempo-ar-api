# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from unittest.mock import call

import mock
from django.test import TestCase
from elasticsearch_dsl import Search, MultiSearch

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.apps.metadata.models import CatalogAlias, MetadataConfig
from series_tiempo_ar_api.apps.metadata.queries.query import FieldSearchQuery
from .utils import get_mock_search

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
mock.patch.object = mock.patch.object  # Hack for pylint inspection


class QueryTests(TestCase):

    def test_no_querystring_is_valid(self):
        query = FieldSearchQuery(args={})

        with mock.patch.object(MultiSearch, 'execute', return_value=get_mock_search()):
            result = query.execute()

        self.assertFalse(result.get('errors'))

    def test_bad_limit(self):
        query = FieldSearchQuery(args={'limit': 'invalid'})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_bad_offset(self):
        query = FieldSearchQuery(args={'start': 'invalid'})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_bad_sort_by(self):
        query = FieldSearchQuery(args={'sort_by': 'invalid'})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_bad_sort(self):
        query = FieldSearchQuery(args={'sort': 'invalid'})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_query_response_size(self):
        query = FieldSearchQuery(args={'q': 'aceite'})

        with mock.patch.object(MultiSearch, 'execute', return_value=get_mock_search()):
            result = query.execute()

        self.assertEqual(len(result['data']), result['count'])

    def test_response_params(self):
        limit = '10'
        offset = '15'
        query = FieldSearchQuery(args={'q': 'aceite',
                                       'limit': limit,
                                       'start': offset})

        with mock.patch.object(MultiSearch, 'execute', return_value=get_mock_search()):
            result = query.execute()

        self.assertEqual(result['limit'], int(limit))
        self.assertEqual(result['start'], int(offset))

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
        with mock.patch.object(MultiSearch, 'execute', return_value=get_mock_search()):
            result = q.execute()

        self.assertTrue(result['data'][0]['field']['frequency'], mock_search.periodicity)
        self.assertTrue(result['data'][0]['field']['time_index_start'], mock_search.start_date)
        self.assertTrue(result['data'][0]['field']['time_index_end'], mock_search.end_date)

    def test_catalog_id_filter_with_alias(self):
        alias = CatalogAlias.objects.create(alias='alias_id')
        alias.nodes.create(catalog_id='catalog_1', catalog_url='http://example.com/1', indexable=True)
        alias.nodes.create(catalog_id='catalog_2', catalog_url='http://example.com/2', indexable=True)
        q = FieldSearchQuery(args={'catalog_id': 'alias_id'})

        search = Search()
        filtered_search = q.add_filters(search, 'catalog_id', 'catalog_id')

        filtered_catalogs = filtered_search.to_dict()['query']['bool']['filter'][0]['terms']['catalog_id']
        self.assertEqual(set(filtered_catalogs), {'catalog_1', 'catalog_2'})

    @mock.patch('series_tiempo_ar_api.apps.metadata.queries.query.MultiSearch.execute')
    def test_no_aggregations_if_not_requested(self, execute):
        execute.return_value = [mock.MagicMock()]
        resp = FieldSearchQuery(args={}).execute()

        self.assertNotIn('aggregations', resp)

    def test_min_score(self):
        query = FieldSearchQuery(args={'limit': 0, 'start': 0, 'q': 'hola'})

        search = query.get_search()
        min_score = search.to_dict()['min_score']
        self.assertEqual(min_score, MetadataConfig.get_solo().min_score)

    def test_min_score_not_added_without_querystring(self):
        query = FieldSearchQuery(args={'limit': 0, 'start': 0})

        search = query.get_search()
        self.assertNotIn('min_score', search.to_dict())

    def test_sort_by_not_added_if_relevance_specified(self):
        query = FieldSearchQuery(args={'sort_by': 'relevance'})

        search = query.get_search()
        self.assertNotIn('sort', search.to_dict().keys())

    def test_default_sorting_can_not_be_ascending(self):
        query = FieldSearchQuery(args={'sort': 'asc'})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_descending_sort_by_hits_90_days_with_default_order(self):
        query = FieldSearchQuery(args={'sort_by': 'hits_90_days'})

        search = query.get_search()
        sort_field = search.to_dict()['sort'][0]

        expected_sort_dict = {'hits': {'order': 'desc'}}
        self.assertDictEqual(expected_sort_dict, sort_field)

    def test_ascending_sort_by_hits_90_days_with_specified_order(self):
        query = FieldSearchQuery(args={'sort_by': 'hits_90_days', 'sort': 'asc'})

        search = query.get_search()
        sort_list = search.to_dict()['sort']
        # Como no es el campo _score, no hace falta especificarle un "order" y puede ser un string

        expected_sort_list = ['hits']
        self.assertListEqual(expected_sort_list, sort_list)

    def test_descending_sort_by_frequency_with_default_order(self):
        query = FieldSearchQuery(args={'sort_by': 'frequency'})

        search = query.get_search()
        sort_field = search.to_dict()['sort'][0]

        expected_sort_dict = {'periodicity_index': {'order': 'desc'}}
        self.assertDictEqual(expected_sort_dict, sort_field)

    def test_ascending_sort_by_frequency_with_specified_order(self):
        query = FieldSearchQuery(args={'sort_by': 'frequency', 'sort': 'asc'})

        search = query.get_search()
        sort_list = search.to_dict()['sort']
        # Como no es el campo _score, no hace falta especificarle un "order" y puede ser un string

        expected_sort_list = ['periodicity_index']
        self.assertListEqual(expected_sort_list, sort_list)
