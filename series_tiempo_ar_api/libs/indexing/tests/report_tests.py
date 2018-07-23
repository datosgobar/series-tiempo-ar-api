#! coding: utf-8
import os
import datetime
from django.test import TestCase
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.libs.indexing.report.report_generator import ReportGenerator

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class ReportTests(TestCase):

    def setUp(self):
        self.task = ReadDataJsonTask.objects.create()
        Node.objects.create(
            catalog_id='test_catalog',
            catalog_url=os.path.join(SAMPLES_DIR, 'broken_catalog.json'),
            indexable=True
        )

    def test_report_broken_catalog(self):
        ReportGenerator(self.task).generate()
        self.task.refresh_from_db()

        self.assertTrue('error' in self.task.logs.lower())
