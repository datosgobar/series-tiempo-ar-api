#!coding=utf8

import json

from django.test import TestCase
from django.urls import reverse


class ViewTests(TestCase):

    def test_response_format(self):
        response = self.client.get(reverse('metadata:search'),
                                   data={'q': 'algodon'})

        response_json = json.loads(response.content)
        self.assertIn('data', response_json)
        self.assertIn('limit', response_json)
        self.assertIn('count', response_json)
        self.assertIn('offset', response_json)
