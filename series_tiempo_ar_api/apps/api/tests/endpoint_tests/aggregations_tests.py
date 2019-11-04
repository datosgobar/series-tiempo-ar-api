import nose

from series_tiempo_ar_api.apps.api.tests.endpoint_tests.endpoint_test_case import EndpointTestCase


class AggregationsTests(EndpointTestCase):

    def _run_test_case(self, params, expected_value):
        response = self.run_query(params)
        value = response['data'][0][1]
        nose.tools.assert_equal(value, expected_value)

    def test_cases(self):
        cases = [
            (self.increasing_day_series_id, 'month', 99+31),
            (self.increasing_day_series_id, 'quarter', 99+31+28+31),
            (self.increasing_day_series_id, 'semester', 99+31+28+31+30+31+30),
            (self.increasing_day_series_id, 'year', 99+365),
            (self.increasing_month_series_id, 'month', 100),
            (self.increasing_month_series_id, 'quarter', 102),
            (self.increasing_month_series_id, 'semester', 105),
            (self.increasing_month_series_id, 'year', 111),
        ]
        for series_id, collapse, expected_value in cases:
            params = {
                'ids': series_id,
                'collapse': collapse,
                'limit': 1,
                'collapse_aggregation': 'max'
            }

            yield self._run_test_case, params, expected_value
