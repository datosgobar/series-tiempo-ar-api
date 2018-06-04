#!coding=utf8
from django.test import TestCase
from django.urls import reverse, exceptions
from django.core.management import call_command
from nose.tools import raises

from series_tiempo_ar_api.apps.dump.models import DumpFile


class ViewTests(TestCase):

    valid_arg = 'series-tiempo-csv.zip'

    def setUp(self):
        DumpFile.objects.all().delete()

    def test_dump_endpoint_not_available(self):
        resp = self.client.get(reverse('api:dump:global_dump', kwargs={'filename': self.valid_arg}))

        self.assertEqual(resp.status_code, 501)

    def test_dump_endpoint_generated(self):
        call_command('generate_dump')
        resp = self.client.get(reverse('api:dump:global_dump', kwargs={'filename': self.valid_arg}))

        self.assertEqual(resp.status_code, 200)

    @raises(exceptions.NoReverseMatch)
    def test_dump_invalid(self):
        call_command('generate_dump')
        self.client.get(reverse('api:dump:global_dump', kwargs={'filename': 'invalid'}))
