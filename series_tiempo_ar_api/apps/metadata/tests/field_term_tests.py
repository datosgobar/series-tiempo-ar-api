#! coding: utf-8

import mock
from django.test import TestCase
from elasticsearch_dsl import Search
from nose.tools import raises

from series_tiempo_ar_api.apps.metadata.queries.query_terms import query_field_terms


class FieldTermsTest(TestCase):

    def test_run(self):
        test_value = 'test_value'
        search_mock = mock.MagicMock()
        search_mock.aggregations.results.buckets = [{'key': test_value, 'doc_count': 1}]

        with mock.patch.object(Search, 'execute', return_value=search_mock):
            terms = query_field_terms(field='test_field')['data']
            result = terms[0]['label']
            self.assertEqual(test_value, result)

    @raises(ValueError)
    def test_no_params(self):
        query_field_terms()
