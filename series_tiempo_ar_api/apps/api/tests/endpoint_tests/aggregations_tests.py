from series_tiempo_ar_api.apps.api.tests.endpoint_tests.endpoint_test_case import EndpointTestCase


class AggregationsTests(EndpointTestCase):

    def test_max_aggregation(self):
        max_value = 130

        data = {'ids': self.increasing_day_series_id,
                'limit': '1',
                'collapse': 'month',
                'collapse_aggregation': 'max'}

        resp = self.run_query(data)
        aggregated_max = resp['data'][0][1]
        self.assertEqual(max_value, aggregated_max)

    def test_min_aggregation(self):
        min_value = 100

        data = {'ids': self.increasing_day_series_id,
                'limit': '1',
                'collapse': 'month',
                'collapse_aggregation': 'min'}

        resp = self.run_query(data)
        aggregated_min = resp['data'][0][1]
        self.assertEqual(min_value, aggregated_min)
