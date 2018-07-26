#!coding=utf8
from decimal import Decimal

from faker import Faker
from django.test import TestCase
from series_tiempo_ar_api.apps.analytics.tasks import import_analytics_from_api_mgmt
from series_tiempo_ar_api.apps.analytics.models import ImportConfig, Query, AnalyticsImportTask

fake = Faker()


class UninitializedImportConfigTests(TestCase):

    def test_not_initialized_model(self):
        import_analytics_from_api_mgmt()
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

    def get(self, *_, **__):
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
        import_analytics_from_api_mgmt(requests_lib=FakeRequests([{
            'next': None,
            'count': 0,
            'results': []
        }]))

        self.assertEqual(Query.objects.count(), 0)

    def test_single_page_results(self):
        import_analytics_from_api_mgmt(requests_lib=FakeRequests([
            {
                'next': None,
                'count': 1,
                'results': [
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:00-03:00',
                        'id': 1,
                        'uri': '/series/api/series/',
                    }
                ]
            }
        ]))
        self.assertEqual(Query.objects.count(), 1)

    def test_many_results(self):
        import_analytics_from_api_mgmt(requests_lib=FakeRequests([
            {
                'next': None,
                'count': 1,
                'results': [
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:00-03:00',
                        'id': 1,
                        'uri': '/series/api/series/',
                    },
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:01-03:00',
                        'id': 2,
                        'uri': '/series/api/series/',
                    }
                ]
            }
        ]))
        self.assertEqual(Query.objects.count(), 2)

    def test_import_all_flag(self):
        self.test_many_results()

        # Borro un dato, y me aseguro que se regenera con import_all
        Query.objects.first().delete()
        import_analytics_from_api_mgmt(requests_lib=FakeRequests([
            {
                'next': None,
                'count': 1,
                'results': [
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:00-03:00',
                        'id': 1,
                        'uri': '/series/api/series/',
                    },
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-08T05:00:01-03:00',
                        'id': 2,
                        'uri': '/series/api/series/',
                    }
                ]
            }
        ]), import_all=True)
        self.assertEqual(Query.objects.count(), 2)

    def test_without_import_all_model_is_not_recreated(self):
        self.test_many_results()

        # Borro un dato. Si no le paso import_all=True, no se va a crear de nuevo
        Query.objects.all().order_by('-timestamp').last().delete()
        import_analytics_from_api_mgmt(requests_lib=FakeRequests([
            {
                'next': None,
                'count': 0,
                'results': [
                ]
            }
        ]), import_all=False)
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
                    'id': 2,
                    'uri': '/series/api/series/',
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
                    'id': 3,
                    'uri': '/series/api/series/',
                }
            ]
        }]
        import_analytics_from_api_mgmt(requests_lib=FakeRequests(responses=return_value))

        self.assertEqual(Query.objects.count(), 2)

    def test_run_import_twice(self):
        results = [
            {
                'next': None,
                'count': 1,
                'results': [
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:00-03:00',
                        'id': 1,
                        'uri': '/series/api/series/',
                    }
                ]
            }
        ]
        import_analytics_from_api_mgmt(requests_lib=FakeRequests(results))
        import_analytics_from_api_mgmt(requests_lib=FakeRequests(results))
        # Esperado: que haya un solo objeto query, no se dupliquen los resultados
        self.assertEqual(Query.objects.count(), 1)

    def test_ignore_not_series_uri(self):
        import_analytics_from_api_mgmt(requests_lib=FakeRequests([
            {
                'next': None,
                'count': 1,
                'results': [
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:00-03:00',
                        'id': 1,
                        'uri': '/series/not_series_endpoint/',
                    }
                ]
            }
        ]))
        self.assertEqual(Query.objects.count(), 0)

    def test_import_uri_field(self):
        uri = '/series/api/series'
        import_analytics_from_api_mgmt(requests_lib=FakeRequests([
            {
                'next': None,
                'count': 1,
                'results': [
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:00-03:00',
                        'id': 1,
                        'uri': uri,
                    }
                ]
            }
        ]))
        self.assertEqual(Query.objects.count(), 1)
        self.assertEqual(Query.objects.first().uri, uri)

    def test_import_status_code_field(self):
        status_code = 200
        import_analytics_from_api_mgmt(requests_lib=FakeRequests([
            {
                'next': None,
                'count': 1,
                'results': [
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:00-03:00',
                        'id': 1,
                        'status_code': status_code,
                        'uri': '/series/api/series',
                    }
                ]
            }
        ]))
        self.assertEqual(Query.objects.count(), 1)
        self.assertEqual(Query.objects.first().status_code, status_code)

    def test_import_user_agent_field(self):
        agent = fake.word()
        import_analytics_from_api_mgmt(requests_lib=FakeRequests([
            {
                'next': None,
                'count': 1,
                'results': [
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:00-03:00',
                        'id': 1,
                        'user_agent': agent,
                        'uri': '/series/api/series',
                    }
                ]
            }
        ]))
        self.assertEqual(Query.objects.count(), 1)
        self.assertEqual(Query.objects.first().user_agent, agent)

    def test_import_response_time(self):
        request_time = str(fake.pyfloat(left_digits=1, right_digits=10, positive=True))
        import_analytics_from_api_mgmt(requests_lib=FakeRequests([
            {
                'next': None,
                'count': 1,
                'results': [
                    {
                        'ip_address': '127.0.0.1',
                        'querystring': '',
                        'start_time': '2018-06-07T05:00:00-03:00',
                        'id': 1,
                        'request_time': request_time,
                        'uri': '/series/api/series',
                    }
                ]
            }
        ]))
        self.assertEqual(Query.objects.count(), 1)
        self.assertEqual(Query.objects.first().request_time, Decimal(request_time))
