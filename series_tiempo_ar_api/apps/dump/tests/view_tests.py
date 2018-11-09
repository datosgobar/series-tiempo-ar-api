#!coding=utf8
import os

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.dump.generator.generator import DumpGenerator
from series_tiempo_ar_api.apps.dump.models import DumpFile, GenerateDumpTask
from series_tiempo_ar_api.libs.indexing.constants import INDEX_CREATION_BODY
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.utils.utils import index_catalog

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
        cls.task = GenerateDumpTask()
        cls.task.save()
        gen = DumpGenerator(cls.task)
        gen.generate()

        DumpGenerator(cls.task, cls.catalog_id).generate()

    def test_dump_endpoint_not_available(self):
        DumpFile.objects.all().delete()
        resp = self.client.get(reverse('api:dump:global_dump', kwargs={'filename': self.valid_arg}))

        self.assertEqual(resp.status_code, 404)

    def test_dump_endpoint_generated(self):
        call_command('generate_dump', index=self.index)
        resp = self.client.get(reverse('api:dump:global_dump', kwargs={'filename': self.valid_arg}))

        self.assertEqual(resp.status_code, 302)  # Redirect al link de descarga

    def test_invalid_dump_url(self):
        resp = self.client.get(reverse('api:dump:global_dump', kwargs={'filename': "file_name_no_extension"}))
        self.assertEqual(resp.status_code, 404)

    def test_bad_extension(self):
        resp = self.client.get(reverse('api:dump:global_dump', kwargs={'filename': "series-tiempo.badextension"}))
        self.assertEqual(resp.status_code, 404)

    def test_catalog_dump(self):
        resp = self.client.get(reverse('api:dump:catalog_dump', kwargs={'filename': "series-tiempo-csv.zip",
                                                                        'catalog_id': self.catalog_id}))

        self.assertEqual(resp.status_code, 302)  # Redirect al link de descarga

    def test_invalid_catalog(self):
        resp = self.client.get(reverse('api:dump:catalog_dump', kwargs={'filename': "series-tiempo-csv.zip",
                                                                        'catalog_id': "not_the_catalog"}))

        self.assertEqual(resp.status_code, 404)

    @classmethod
    def tearDownClass(cls):
        super(ViewTests, cls).tearDownClass()
        ElasticInstance.get().indices.delete(cls.index)
        DumpFile.objects.all().delete()
        Node.objects.all().delete()
