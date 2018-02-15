#! coding: utf-8

import mock
import json
from elasticsearch_dsl import Search


from django.test import TestCase
from django.urls import reverse


class DatasetSourceTests(TestCase):

    def test_run(self):
        test_source = 'test_source'
        search_mock = mock.MagicMock()
        search_mock.aggregations.sources.buckets = [{'key': test_source}]

        with mock.patch.object(Search, 'execute', return_value=search_mock):
            response = self.client.get(reverse('api:metadata:dataset_source'))
            response_sources = json.loads(response.content)['sources']
            self.assertIn(test_source, response_sources)
