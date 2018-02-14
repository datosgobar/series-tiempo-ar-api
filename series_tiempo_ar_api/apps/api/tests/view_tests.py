#! coding: utf-8
import json

from django.conf import settings
from django.http import JsonResponse
from django.test import TestCase, Client
from django.urls import reverse

from series_tiempo_ar_api.apps.api.tests.helpers import setup_database

SERIES_NAME = settings.TEST_SERIES_NAME.format('month')


class ViewTests(TestCase):

    client = Client()
    endpoint = reverse('series:series')

    @classmethod
    def setUpClass(cls):
        setup_database()
        super(ViewTests, cls).setUpClass()

    def test_series_default_type(self):
        response = self.client.get(self.endpoint, data={'ids': SERIES_NAME})
        self.assertTrue(type(response) == JsonResponse)

    def test_series_empty_args(self):
        response = json.loads(self.client.get(self.endpoint).content)

        self.assertTrue(response['errors'])

    def test_csv_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': SERIES_NAME, 'format': 'csv'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': SERIES_NAME, 'format': 'CSV'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, response_upper.content)

    def test_collapse_agg_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': SERIES_NAME,
                                         'collapse_aggregation': 'sum'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': SERIES_NAME,
                                               'collapse_aggregation': 'SUM'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, response_upper.content)

    def test_rep_mode_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': SERIES_NAME,
                                         'representation_mode': 'percent_change'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': SERIES_NAME,
                                               'representation_mode': 'PERCENT_change'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, response_upper.content)

    def test_sort_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': SERIES_NAME,
                                         'sort': 'desc'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': SERIES_NAME,
                                               'sort': 'DESC'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, response_upper.content)

    def test_metadata_ignore_case(self):
        response = self.client.get(self.endpoint,
                                   data={'ids': SERIES_NAME,
                                         'metadata': 'none'})
        response_upper = self.client.get(self.endpoint,
                                         data={'ids': SERIES_NAME,
                                               'metadata': 'None'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, response_upper.content)
