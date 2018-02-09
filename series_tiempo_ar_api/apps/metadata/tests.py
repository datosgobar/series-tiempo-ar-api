# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from elasticsearch_dsl import Search
from django.test import TestCase

from series_tiempo_ar_api.apps.metadata.query import FieldMetadataQuery


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

    def test_query(self):
        Search.execute = mock.Mock(return_value=[{'id': 'series_id', 'title': 'title', 'description': 'desc'}])
        query = FieldMetadataQuery(args={'q': 'aceite'})
        result = query.execute()

        self.assertTrue(result['data'])
