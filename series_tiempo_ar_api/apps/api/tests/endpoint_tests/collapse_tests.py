import iso8601

from series_tiempo_ar_api.apps.api.helpers import get_relative_delta
from series_tiempo_ar_api.apps.api.tests.endpoint_tests.endpoint_test_case import EndpointTestCase


class TestCollapse(EndpointTestCase):

    def test_collapse_dates(self):
        cases = [
            (self.increasing_day_series_id, 'month'),
            (self.increasing_day_series_id, 'quarter'),
            (self.increasing_day_series_id, 'semester'),
            (self.increasing_day_series_id, 'year'),
            (self.increasing_month_series_id, 'quarter'),
            (self.increasing_month_series_id, 'semester'),
            (self.increasing_month_series_id, 'year'),
            (self.increasing_quarter_series_id, 'semester'),
            (self.increasing_quarter_series_id, 'year'),
        ]

        for serie_id, collapse in cases:
            params = {
                'ids': serie_id,
                'collapse': collapse,
            }

            yield self._run_query, params

    def _run_query(self, params):
        resp = self.run_query(params)
        current = iso8601.parse_date(resp['data'][0][0])
        for index, _ in resp['data'][1:]:
            date = iso8601.parse_date(index)
            assert current + get_relative_delta(params['collapse']) == date
            current = date
