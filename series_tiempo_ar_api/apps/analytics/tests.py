#! coding: utf-8
import json

from django.test import TestCase

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
