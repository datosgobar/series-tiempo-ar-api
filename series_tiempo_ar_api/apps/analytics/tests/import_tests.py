#!coding=utf8

import mock
from nose.tools import raises
from django.core.exceptions import FieldError
from django.test import TestCase
from series_tiempo_ar_api.apps.analytics.tasks import import_last_day_analytics_from_api_mgmt
from series_tiempo_ar_api.apps.analytics.models import ImportConfig, Query


class UninitializedImportConfigTests(TestCase):

    @raises(FieldError)
    def test_not_initialized_model(self):
        import_last_day_analytics_from_api_mgmt()


def mocked_requests_get():
    class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data

        def __call__(self, *args, **kwargs):
            return self

    return MockResponse(
        {
            'next': None,
            'results': [
                {
                    'ip_address': '127.0.0.1',
                    'querystring': '',
                    'start_time': '2018-06-07T05:00:00-03:00',
                }
            ]
        }
    )


class ImportTests(TestCase):

    def setUp(self):
        config_model = ImportConfig.get_solo()
        config_model.endpoint = 'http://localhost:80/fake_endpoint'
        config_model.token = 'fake-token'
        config_model.kong_api_id = 'fake_id'
        config_model.save()

    def test_single_empty_result(self):
        with mock.patch.object(ImportConfig, 'get_results', return_value={
            'next': None,
            'results': []
        }):
            import_last_day_analytics_from_api_mgmt()

        self.assertEqual(Query.objects.count(), 0)

    def test_single_page_results(self):
        with mock.patch.object(ImportConfig, 'get_results', return_value={
            'next': None,
            'results': [
                {
                    'ip_address': '127.0.0.1',
                    'querystring': '',
                    'start_time': '2018-06-07T05:00:00-03:00',
                }
            ]
        }):
            import_last_day_analytics_from_api_mgmt()
            self.assertEqual(Query.objects.count(), 1)

    def test_multiple_page_results(self):
        """Emula una query con dos páginas de resultados, cada una con una query"""
        return_value = {
            'next': 'next_page_url',
            'results': [
                {
                    'ip_address': '127.0.0.1',
                    'querystring': '',
                    'start_time': '2018-06-07T05:00:00-03:00',
                }
            ]
        }
        with mock.patch.object(ImportConfig, 'get_results', return_value=return_value):
            with mock.patch('series_tiempo_ar_api.apps.analytics.tasks.requests.get',
                            new_callable=mocked_requests_get):
                import_last_day_analytics_from_api_mgmt()

        self.assertEqual(Query.objects.count(), 2)
