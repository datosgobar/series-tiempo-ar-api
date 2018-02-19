#! coding: utf-8
import json
import copy

from django.test import TestCase
from django.urls import reverse

from .analytics import analytics
from .models import Query
from .utils import kong_milliseconds_to_tzdatetime


class AnalyticsTests(TestCase):

    def test_analytics_creates_model(self):
        series_ids = "serie1"
        args = "query_arg=value"
        ip_address = "ip_address"
        args_dict = {'json': 'with_args'}
        timestamp = 1433209822425

        # Expected: la función crea un objeto Query en la base de datos
        analytics(series_ids, args, ip_address, args_dict, timestamp)

        query = Query.objects.get(ids=series_ids,
                                  args=args,
                                  ip_address=ip_address)

        timestamp_datetime = kong_milliseconds_to_tzdatetime(timestamp)

        self.assertTrue(query)
        self.assertEqual(args_dict, json.loads(query.params))
        self.assertEqual(timestamp_datetime, query.timestamp)


class AnalyticsViewTests(TestCase):

    body = {
        'request': {
            'querystring': {'ids': 'test_id'},
            'uri': 'api/series',
            'request_uri': 'http://localhost:8000/api/series?ids=test_id',
        },
        'client_ip': '127.0.0.1',
        'started_at': 1271237123,
    }

    def test_view_valid_body(self):
        count_before = Query.objects.count()
        response = self.client.post(reverse('analytics:save'),
                                    json.dumps(self.body),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Query.objects.count(), count_before + 1)

    def test_view_invalid_method(self):
        response = self.client.put(reverse('analytics:save'),
                                   json.dumps(self.body),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 405)

    def test_view_empty_body(self):
        response = self.client.post(reverse('analytics:save'),
                                    '{}',
                                    content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_admin_call_not_logged(self):
        body = copy.deepcopy(self.body)
        body['request']['uri'] = 'admin/api/dataset/12'
        count_before = Query.objects.count()
        response = self.client.post(reverse('analytics:save'),
                                    json.dumps(body),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

        # Count unchanged
        self.assertEqual(Query.objects.count(), count_before)
