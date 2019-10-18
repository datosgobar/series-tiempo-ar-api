from django.test import TestCase
from mock import patch

from series_tiempo_ar_api.apps.management.tasks.integration_test import run_integration


class IntegrationTestTasksTests(TestCase):

    def test_integration_test_not_started_if_metadata_does_not_exist(self):
        with patch('series_tiempo_ar_api.apps.management.tasks.integration_test.IntegrationTest') as m:
            run_integration()

        m.assert_not_called()
