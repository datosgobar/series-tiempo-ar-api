from django.urls import reverse

from series_tiempo_ar_api.apps.api.tests.endpoint_tests.endpoint_test_case import EndpointTestCase


class PaginationTests(EndpointTestCase):

    def test_get_single_value(self):
        resp = self.client.get(reverse('api:series:series'), data={'ids': self.increasing_month_series_id, 'limit': 1})

        self.assertEqual(len(resp.json()['data']), 1)

    def test_get_five_offset_values(self):
        data = {'ids': self.increasing_month_series_id, 'start': 5, 'limit': 5}
        resp = self.run_query(data)
        data = [
            ['1999-06-01', 105],
            ['1999-07-01', 106],
            ['1999-08-01', 107],
            ['1999-09-01', 108],
            ['1999-10-01', 109],
        ]
        self.assertEqual(resp['data'], data)
