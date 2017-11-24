#! coding: utf-8
import json

from django.http import JsonResponse
from django.test import TestCase, Client
from django.urls import reverse


class ViewTests(TestCase):

    client = Client()
    endpoint = reverse('api:series')

    def test_series_default_type(self):
        response = self.client.get(self.endpoint, data={'ids': 'random_series-month-0'})
        self.assertTrue(type(response) == JsonResponse)

    def test_series_empty_args(self):
        response = json.loads(self.client.get(self.endpoint).content)

        self.assertTrue(response['errors'])

    def test_args_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': 'random_series-month-0', 'format': 'csv'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': 'random_series-month-0', 'format': 'CSV'})

        self.assertEqual(response.content, response_upper.content)
