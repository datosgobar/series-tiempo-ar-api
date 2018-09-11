#!coding=utf8
import os

from django.conf import settings
from django.test import TestCase
from django.urls import reverse, exceptions
from django.core.management import call_command
from django_datajsonar.models import Node
from nose.tools import raises

from series_tiempo_ar_api.apps.dump.generator.generator import DumpGenerator
from series_tiempo_ar_api.apps.dump.models import DumpFile, CSVDumpTask
from series_tiempo_ar_api.libs.indexing.constants import INDEX_CREATION_BODY
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.utils import index_catalog

samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class ViewTests(TestCase):
    directory = os.path.join(settings.MEDIA_ROOT, 'test_dump')
    valid_arg = 'series-tiempo-csv.zip'

    index = 'csv_dump_view_test_index'

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        es_client = ElasticInstance.get()
        if es_client.indices.exists(cls.index):
            es_client.indices.delete(cls.index)
        es_client.indices.create(cls.index, body=INDEX_CREATION_BODY)

        cls.catalog_id = 'csv_dump_test_catalog'
        path = os.path.join(samples_dir, 'distribution_daily_periodicity.json')
        index_catalog(cls.catalog_id, path, cls.index)
        cls.task = CSVDumpTask()
        cls.task.save()
        gen = DumpGenerator(cls.task)
        gen.generate()

    def setUp(self):
        DumpFile.objects.all().delete()

    def test_dump_endpoint_not_available(self):
        resp = self.client.get(reverse('api:dump:global_dump', kwargs={'filename': self.valid_arg}))

        self.assertEqual(resp.status_code, 501)

    def test_dump_endpoint_generated(self):
        call_command('generate_dump', index=self.index)
        resp = self.client.get(reverse('api:dump:global_dump', kwargs={'filename': self.valid_arg}))

        self.assertEqual(resp.status_code, 200)

    @raises(exceptions.NoReverseMatch)
    def test_dump_invalid(self):
        call_command('generate_dump', index=self.index)
        self.client.get(reverse('api:dump:global_dump', kwargs={'filename': 'invalid'}))

    @classmethod
    def tearDownClass(cls):
        ElasticInstance.get().indices.delete(cls.index)
        Node.objects.all().delete()
