from django.test import TestCase

from series_tiempo_ar_api.apps.management.models import APIIndexingConfig


class APIIndexingConfigTests(TestCase):

    def test_has_task_timeout_default(self):
        default_value = 1000

        self.assertEqual(APIIndexingConfig.get_solo().indexing_timeout, default_value)
