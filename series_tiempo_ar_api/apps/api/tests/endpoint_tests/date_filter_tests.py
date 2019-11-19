import iso8601
import nose

from series_tiempo_ar_api.apps.api.tests.endpoint_tests.endpoint_test_case import EndpointTestCase


class TestDateFilters(EndpointTestCase):

    def setUp(self):
        self.start_date = '2010-01-01'
        self.end_date = '2015-01-01'

    def test_filters(self):
        resp = self.run_query({'ids': self.increasing_month_series_id,
                               'start_date': '2010-01-01',
                               'end_date': '2015-01-01'})

        for row in resp['data']:
            if 'T' in row[0]:
                date = iso8601.parse_date(row[0])
                start_date = iso8601.parse_date(self.start_date)
                end_date = iso8601.parse_date(self.end_date)
            else:
                date = iso8601.parse_date(row[0])
                start_date = iso8601.parse_date(self.start_date)
                end_date = iso8601.parse_date(self.end_date)
            nose.tools.assert_greater_equal(date, start_date)

            nose.tools.assert_less_equal(date, end_date)
