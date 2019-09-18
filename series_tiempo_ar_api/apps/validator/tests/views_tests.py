#! coding: utf-8
import json

from django.test import TestCase, RequestFactory
from django.urls import reverse

BASE_URL = \
    "http://localhost:3456/series_tiempo_ar_api/apps/validator/tests/samples/"


class ValidatorViewTests(TestCase):
    endpoint = reverse('api:validator:validator')

    def setUp(self):
        self.request_data = {
            "catalog_url": BASE_URL + "valid_catalog.json",
            "distribution_id": "125.1"
        }
        self.factory = RequestFactory()
        super(ValidatorViewTests, self).setUp()

    def test_response_type(self):
        response = self.client.post(self.endpoint,
                                    json.dumps(self.request_data),
                                    content_type='application/json')
        self.assertEqual(200, response.status_code)

    def test_valid_series(self):
        response = self.client.post(self.endpoint,
                                    json.dumps(self.request_data),
                                    content_type='application/json')
        response_body = json.loads(response.content.decode('utf8'))
        self.assertEqual(BASE_URL + "valid_catalog.json",
                         response_body['catalog_url'])
        self.assertEqual('125.1', response_body['distribution_id'])
        self.assertEqual(0, response_body['found_issues'])
        self.assertListEqual([], response_body['detail'])

    def test_data_error_series(self):
        self.request_data.update(
            {'catalog_url':
             BASE_URL + "distribution_missing_column_in_data.json"})
        response = self.client.post(self.endpoint,
                                    json.dumps(self.request_data),
                                    content_type='application/json')
        response_body = json.loads(response.content.decode('utf8'))
        self.assertEqual(BASE_URL + "distribution_missing_column_in_data.json",
                         response_body['catalog_url'])
        self.assertEqual('125.1', response_body['distribution_id'])
        self.assertEqual(1, response_body['found_issues'])
        self.assertListEqual(
            ['Campo title2 faltante en la distribución 125.1'],
            response_body['detail'])

    def test_metadata_error_series(self):
        self.request_data.update(
            {'catalog_url': BASE_URL + "repeated_field_id.json"})
        response = self.client.post(self.endpoint,
                                    json.dumps(self.request_data),
                                    content_type='application/json')
        response_body = json.loads(response.content.decode('utf8'))
        self.assertEqual(BASE_URL + "repeated_field_id.json",
                         response_body['catalog_url'])
        self.assertEqual('125.1', response_body['distribution_id'])
        self.assertEqual(1, response_body['found_issues'])
        self.assertListEqual(
            ['Hay field con id repetido: id_serie_1'],
            response_body['detail'])

    def test_multiple_error_series(self):
        self.request_data.update(
            {'catalog_url': BASE_URL + "repeated_field_id_and_description.json"})
        response = self.client.post(self.endpoint,
                                    json.dumps(self.request_data),
                                    content_type='application/json')
        response_body = json.loads(response.content.decode('utf8'))
        self.assertEqual(BASE_URL + "repeated_field_id_and_description.json",
                         response_body['catalog_url'])
        self.assertEqual('125.1', response_body['distribution_id'])
        self.assertEqual(2, response_body['found_issues'])
        self.assertSetEqual({
            'Hay field con id repetido: id_serie_1',
            "Hay field con description repetido: ['Descripción de la serie 1']"
        }, set(response_body['detail']))

    def test_missing_catalog_request(self):
        del self.request_data['catalog_url']
        response = self.client.post(self.endpoint,
                                    json.dumps(self.request_data),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_missing_distribution_request(self):
        del self.request_data['distribution_id']
        response = self.client.post(self.endpoint,
                                    json.dumps(self.request_data),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_http_request_not_allowed(self):
        not_allowed_methods = [
            self.client.get,
            self.client.head,
            self.client.patch,
            self.client.put,
        ]
        for method in not_allowed_methods:
            response = method(self.endpoint)
            self.assertEqual(405, response.status_code)

    def test_xlsx_catalog(self):
        self.request_data.update(
            {'catalog_url': BASE_URL + "catalog.xlsx",
             'distribution_id': '221859a8-c51e-47c2-95ab-a8525bb2b55d',
             'catalog_format': 'xlsx'}
        )
        response = self.client.post(self.endpoint,
                                    json.dumps(self.request_data),
                                    content_type='application/json')
        response_body = json.loads(response.content.decode('utf8'))
        self.assertEqual(BASE_URL + "catalog.xlsx",
                         response_body['catalog_url'])
        self.assertEqual('221859a8-c51e-47c2-95ab-a8525bb2b55d',
                         response_body['distribution_id'])
        self.assertEqual(1, response_body['found_issues'])
        self.assertListEqual(
            ['Campo superficie_ha_santa_fe faltante en la distribución 221859a8-c51e-47c2-95ab-a8525bb2b55d'],
            response_body['detail'])
