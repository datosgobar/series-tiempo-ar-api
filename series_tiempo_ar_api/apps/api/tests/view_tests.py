#! coding: utf-8
import json

from django.http import JsonResponse
from django.test import TestCase, Client
from django.urls import reverse

from series_tiempo_ar_api.apps.api.tests.helpers import setup_database


class ViewTests(TestCase):

    client = Client()
    endpoint = reverse('api:series')

    @classmethod
    def setUpClass(cls):
        setup_database()
        super(ViewTests, cls).setUpClass()

    def test_series_default_type(self):
        response = self.client.get(self.endpoint, data={'ids': 'random_series-month-0'})
        self.assertTrue(type(response) == JsonResponse)

    def test_series_empty_args(self):
        response = json.loads(self.client.get(self.endpoint).content)

        self.assertTrue(response['errors'])

    def test_csv_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': 'random_series-month-0', 'format': 'csv'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': 'random_series-month-0', 'format': 'CSV'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, response_upper.content)

    def test_collapse_agg_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': 'random_series-month-0',
                                         'collapse_aggregation': 'sum'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': 'random_series-month-0',
                                               'collapse_aggregation': 'SUM'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, response_upper.content)

    def test_rep_mode_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': 'random_series-month-0',
                                         'representation_mode': 'percent_change'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': 'random_series-month-0',
                                               'representation_mode': 'PERCENT_change'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, response_upper.content)

    def test_sort_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': 'random_series-month-0',
                                         'sort': 'desc'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': 'random_series-month-0',
                                               'sort': 'DESC'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, response_upper.content)

    def test_metadata_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': 'random_series-month-0',
                                         'metadata': 'none'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': 'random_series-month-0',
                                               'metadata': 'None'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, response_upper.content)
