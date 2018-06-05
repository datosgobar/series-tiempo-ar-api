#!coding=utf8
from django.test import TestCase
from django.urls import reverse, exceptions
from django.core.management import call_command
from nose.tools import raises

from series_tiempo_ar_api.apps.dump.models import DumpFile
from series_tiempo_ar_api.libs.indexing.constants import INDEX_CREATION_BODY
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class ViewTests(TestCase):
    valid_arg = 'series-tiempo-csv.zip'

    index = 'csv_dump_view_test_index'

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        ElasticInstance.get().indices.create(cls.index, body=INDEX_CREATION_BODY)

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
