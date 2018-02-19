#!coding=utf8
import os

from django.test import TestCase
from django.utils import timezone

from series_tiempo_ar_api.apps.analytics.models import Query
from series_tiempo_ar_api.apps.analytics.tasks import export


class ExportTests(TestCase):

    filepath = 'test'

    def test_export(self):
        Query(args='test', params='test', ip_address='ip_addr', timestamp=timezone.now(), ids='').save()

        export(path=self.filepath)

        with open(self.filepath) as f:
            self.assertEqual(len(f.readlines()), 2)

    def test_export_empty(self):
        export(path=self.filepath)

        with open(self.filepath) as f:
            # Esperado solo una línea de header
            self.assertEqual(len(f.readlines()), 1)

    def tearDown(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
