#!coding=utf8

import json

import mock
from django.test import TestCase
from django.urls import reverse
from elasticsearch_dsl.search import Search

from .utils import get_mock_search


class ViewTests(TestCase):

    def test_response_format(self):
        with mock.patch.object(Search, 'execute', return_value=get_mock_search()):
            response = self.client.get(reverse('api:metadata:search'),
                                       data={'q': 'algodon'})

        response_json = json.loads(response.content)
        self.assertIn('data', response_json)
        self.assertIn('limit', response_json)
        self.assertIn('count', response_json)
        self.assertIn('offset', response_json)


class DatasetSourceTests(TestCase):

    def test_run(self):
        test_source = 'test_source'
        search_mock = mock.MagicMock()
        search_mock.aggregations.results.buckets = [{'key': test_source}]

        with mock.patch.object(Search, 'execute', return_value=search_mock):
            response = self.client.get(reverse('api:metadata:dataset_source'))
            response_sources = json.loads(response.content)['data']
            self.assertIn(test_source, response_sources)


class FieldUnitTests(TestCase):

    def test_run(self):
        test_unit = 'test_unit'
        search_mock = mock.MagicMock()
        search_mock.aggregations.results.buckets = [{'key': test_unit}]

        with mock.patch.object(Search, 'execute', return_value=search_mock):
            response = self.client.get(reverse('api:metadata:field_units'))
            response_sources = json.loads(response.content)['data']
            # Expected: search results in 'data' list
            self.assertIn(test_unit, response_sources)


class PublisherNameTests(TestCase):

    def test_run(self):
        test_unit = 'Test publisher name'
        search_mock = mock.MagicMock()
        search_mock.aggregations.results.buckets = [{'key': test_unit}]

        with mock.patch.object(Search, 'execute', return_value=search_mock):
            response = self.client.get(reverse('api:metadata:dataset_publisher_name'))
            response_sources = json.loads(response.content)['data']
            # Expected: search results in 'data' list
            self.assertIn(test_unit, response_sources)
