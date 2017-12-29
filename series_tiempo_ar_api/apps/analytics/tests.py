#! coding: utf-8
import json

from django.test import TestCase

from .analytics import analytics
from .models import Query


class AnalyticsTests(TestCase):

    def test_analytics_creates_model(self):
        series_ids = "serie1"
        args = "query_arg=value"
        ip_address = "ip_address"
        args_dict = {'json': 'with_args'}

        # Expected: la función crea un objeto Query en la base de datos
        analytics(series_ids, args, ip_address, args_dict)

        query = Query.objects.get(ids=series_ids,
                                  args=args,
                                  ip_address=ip_address)

        self.assertTrue(query)
        self.assertEqual(args_dict, json.loads(query.params))
