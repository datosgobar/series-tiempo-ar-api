#!coding=utf8

from django.test import TestCase
from series_tiempo_ar_api.apps.analytics.tasks import import_last_day_analytics_from_api_mgmt
from series_tiempo_ar_api.apps.analytics.models import ImportConfig, Query, AnalyticsImportTask


class UninitializedImportConfigTests(TestCase):

    def test_not_initialized_model(self):
        import_last_day_analytics_from_api_mgmt()
        self.assertTrue('Error' in AnalyticsImportTask.objects.last().logs)


class FakeRequests:

    class Response:
        def __init__(self, response):
            self.response = response

        def json(self):
            return self.response

    def __init__(self, responses):
        self.responses = responses
        self.index = 0

    def get(self, *args, **kwargs):
        response = self.Response(self.responses[self.index])
        self.index += 1
        return response


class ImportTests(TestCase):

    def setUp(self):
        config_model = ImportConfig.get_solo()
        config_model.endpoint = 'http://localhost:80/fake_endpoint'
        config_model.token = 'fake-token'
        config_model.kong_api_id = 'fake_id'
        config_model.save()

    def test_single_empty_result(self):
        import_last_day_analytics_from_api_mgmt(requests_lib=FakeRequests([{
            'next': None,
            'count': 0,
            'results': []
        }]))

        self.assertEqual(Query.objects.count(), 0)

    def test_single_page_results(self):
        import_last_day_analytics_from_api_mgmt(requests_lib=FakeRequests([
            {
                'next': None,
                'count': 1,
                'results': [
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:00-03:00',
                    }
                ]
            }
        ]))
        self.assertEqual(Query.objects.count(), 1)

    def test_multiple_page_results(self):
        """Emula una query con dos páginas de resultados, cada una con una query"""
        return_value = [{
            'next': 'next_page_url',
            'count': 2,
            'results': [
                {
                    'ip_address': '127.0.0.1',
                    'querystring': '',
                    'start_time': '2018-06-07T05:00:00-03:00',
                }
            ]
        }, {
            'next': None,
            'count': 2,
            'results': [
                {
                    'ip_address': '127.0.0.1',
                    'querystring': '',
                    'start_time': '2018-06-07T05:00:00-03:00',
                }
            ]
        }]
        import_last_day_analytics_from_api_mgmt(requests_lib=FakeRequests(responses=return_value))

        self.assertEqual(Query.objects.count(), 2)
