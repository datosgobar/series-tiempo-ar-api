# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import mock
from elasticsearch_dsl import Search
from pydatajson import DataJson
from django.test import TestCase

from series_tiempo_ar_api.apps.metadata.query import FieldMetadataQuery
from series_tiempo_ar_api.apps.metadata.indexer import constants

from series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer import MetadataIndexer

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
mock.patch.object = mock.patch.object  # Hack for pylint inspection


class QueryTests(TestCase):

    def test_no_querystring(self):
        query = FieldMetadataQuery(args={})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_bad_limit(self):
        query = FieldMetadataQuery(args={'limit': 'invalid'})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_bad_offset(self):
        query = FieldMetadataQuery(args={'offset': 'invalid'})

        result = query.execute()

        self.assertTrue(result['errors'])

    def test_query_response_size(self):
        query = FieldMetadataQuery(args={'q': 'aceite'})
        return_value = [{
            'id': 'algo',
            'description': 'description',
            'title': 'title',
        }]
        with mock.patch.object(Search, 'execute', return_value=return_value):
            result = query.execute()

        self.assertEqual(len(result['data']), result['count'])

    def test_response_params(self):
        limit = '10'
        offset = '15'
        query = FieldMetadataQuery(args={'q': 'aceite',
                                         'limit': limit,
                                         'offset': offset})
        return_value = [{
            'id': 'algo',
            'description': 'description',
            'title': 'title',
        }]
        with mock.patch.object(Search, 'execute', return_value=return_value):
            result = query.execute()

        self.assertEqual(result['limit'], int(limit))
        self.assertEqual(result['offset'], int(offset))


class IndexerTests(TestCase):

    def setUp(self):
        # No mandar datos a la instancia de ES
        MetadataIndexer.init_index = mock.Mock()
        MetadataIndexer.index_actions = mock.Mock()

    def test_scraping(self):
        catalog = os.path.join(SAMPLES_DIR, 'single_distribution.json')
        datajson = DataJson(catalog)
        result = MetadataIndexer().scrap_datajson(datajson)

        self.assertEqual(len(result), len(datajson.get_fields()) - 1)

    def test_scraping_result(self):
        catalog = os.path.join(SAMPLES_DIR, 'single_distribution.json')
        datajson = DataJson(catalog)
        result = MetadataIndexer().scrap_datajson(datajson)

        mapping = constants.FIELDS_MAPPING['mappings']
        mapping_fields = mapping[constants.FIELDS_DOC_TYPE]['properties'].keys()

        # Me aseguro que los resultados sean legibles por el indexer de ES
        for field in result:
            for key in field['_source'].keys():
                self.assertIn(key, mapping_fields)

            self.assertEqual(field['_type'], constants.FIELDS_DOC_TYPE)
            self.assertEqual(field['_index'], constants.FIELDS_INDEX)
