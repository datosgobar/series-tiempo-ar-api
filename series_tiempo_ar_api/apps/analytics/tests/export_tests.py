#!coding=utf8
import os

import csv
from django.utils.timezone import localtime
from iso8601 import iso8601
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

    def test_export_dates(self):
        query = Query(args='test', params='test', ip_address='ip_addr', timestamp=timezone.now(), ids='')
        query.save()

        export(path=self.filepath)
        with open(self.filepath) as f:
            next(f)
            for line in csv.reader(f):
                date = iso8601.parse_date(line[0])
                # Timestamp del modelo en UTC, pasandola a localtime debe ser igual a la del CSV
                self.assertEqual(localtime(query.timestamp), date)
