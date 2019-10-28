from django.conf import settings
from django.test import TestCase
from django.urls import reverse


a = {
    'series_id': 'month_series'
}


class EndpointTests(TestCase):
    def test_something(self):
        resp = self.client.get(reverse('api:series:series'))
        self.assertEqual(resp.status_code, 400)

    def test_real(self):

        data = {'ids': settings.TEST_SERIES_NAME.format('month')}
        resp = self.client.get(reverse('api:series:series'), data=data)
        self.assertTrue(resp.json().get('data'))
