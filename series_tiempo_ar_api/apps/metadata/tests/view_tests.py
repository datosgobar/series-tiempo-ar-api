#!coding=utf8

import json

import mock
from django.test import TestCase
from django.urls import reverse
from elasticsearch_dsl.search import Search


class ViewTests(TestCase):

    def test_response_format(self):
        with mock.patch.object(Search, 'execute', return_value=[]):
            response = self.client.get(reverse('metadata:search'),
                                       data={'q': 'algodon'})

        response_json = json.loads(response.content)
        self.assertIn('data', response_json)
        self.assertIn('limit', response_json)
        self.assertIn('count', response_json)
        self.assertIn('offset', response_json)
