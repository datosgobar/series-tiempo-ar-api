import nose

from series_tiempo_ar_api.apps.api.tests.endpoint_tests.endpoint_test_case import EndpointTestCase


class TestAggregations(EndpointTestCase):

    def _run_test_case(self, params, expected_value):
        response = self.run_query(params)
        value = response['data'][0][1]
        nose.tools.assert_equal(value, expected_value)

    def test_cases(self):
        cases = [
            (self.increasing_day_series_id, 'month', 99 + 31),
            (self.increasing_day_series_id, 'quarter', 99 + 31 + 28 + 31),
            (self.increasing_day_series_id, 'year', 99 + 365),
            (self.increasing_month_series_id, 'month', 100),
            (self.increasing_month_series_id, 'quarter', 102),
            (self.increasing_month_series_id, 'year', 111),
            (self.increasing_quarter_series_id, 'year', 103),
        ]
        for series_id, collapse, expected_value in cases:
            params = {
                'ids': series_id,
                'collapse': collapse,
                'limit': 1,
                'collapse_aggregation': 'max'
            }

            yield self._run_test_case, params, expected_value

            # Serie es creciente, entonces max == end_of_period
            params['collapse_aggregation'] = 'end_of_period'
            yield self._run_test_case, params, expected_value

            # Serie es creciente, entonces min == primer valor == 100
            params['collapse_aggregation'] = 'min'
            yield self._run_test_case, params, 100

    def test_end_of_period_with_rep_mode(self):
        params = {
            'ids': self.increasing_month_series_id,
            'collapse': 'year',
            'limit': 10,
            'collapse_aggregation': 'end_of_period'
        }
        resp = self.run_query(params)
        expected = [
            ['1999-01-01', 111],
            ['2000-01-01', 123],
            ['2001-01-01', 135],
            ['2002-01-01', 147],
            ['2003-01-01', 159],
            ['2004-01-01', 171],
            ['2005-01-01', 183],
            ['2006-01-01', 195],
            ['2007-01-01', 207],
            ['2008-01-01', 219],
        ]
        assert resp['data'] == expected

    def test_sum(self):
        cases = [
            (self.increasing_day_series_id, 'month', sum(range(100, 131))),
            (self.increasing_day_series_id, 'quarter', sum(range(100, 100 + 31 + 28 + 31))),
            (self.increasing_day_series_id, 'semester', sum(range(100, 281))),
            (self.increasing_day_series_id, 'year', sum(range(100, 465))),
            (self.increasing_month_series_id, 'quarter', sum(range(100, 103))),
            (self.increasing_month_series_id, 'semester', sum(range(100, 106))),
            (self.increasing_month_series_id, 'year', sum(range(100, 112))),
            (self.increasing_quarter_series_id, 'semester', sum(range(100, 102))),
            (self.increasing_quarter_series_id, 'year', sum(range(100, 104))),
        ]

        for series_id, collapse, expected in cases:
            params = {
                'ids': series_id,
                'collapse': collapse,
                'limit': 1,
                'collapse_aggregation': 'sum'
            }

            yield self._run_test_case, params, expected

    def test_average(self):

        cases = [
            (self.increasing_day_series_id, 'month', self._avg(range(100, 131))),
            (self.increasing_day_series_id, 'quarter', self._avg(range(100, 100 + 31 + 28 + 31))),
            (self.increasing_day_series_id, 'semester', self._avg(range(100, 281))),
            (self.increasing_day_series_id, 'year', self._avg(range(100, 465))),
            (self.increasing_month_series_id, 'quarter', self._avg(range(100, 103))),
            (self.increasing_month_series_id, 'semester', self._avg(range(100, 106))),
            (self.increasing_month_series_id, 'year', self._avg(range(100, 112))),
            (self.increasing_quarter_series_id, 'semester', self._avg(range(100, 102))),
            (self.increasing_quarter_series_id, 'year', self._avg(range(100, 104))),
        ]

        for series_id, collapse, expected in cases:
            params = {
                'ids': series_id,
                'collapse': collapse,
                'limit': 1,
                'collapse_aggregation': 'avg'
            }

            yield self._run_test_case, params, expected

    def _avg(self, values):
        return sum(values) / len(values)

    def test_aggregations_on_yearly_series(self):
        aggs = ['sum', 'avg', 'end_of_period', 'max', 'min']

        for agg in aggs:
            params = {
                'ids': f'{self.increasing_year_series_id}:{agg},{self.increasing_year_series_id}',
                'collapse': 'year',
            }
            yield self._run_comparison_test, params

    def _run_comparison_test(self, params):
        resp = self.run_query(params)
        for row in resp['data']:
            nose.tools.assert_equals(row[1], row[2])
