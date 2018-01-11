#! coding: utf-8

from django.test import TestCase
from django.core.management import call_command
from StringIO import StringIO

from ..models import Node


class ReadDataJsonTests(TestCase):

    def setUp(self):
        Node(catalog_id='justicia',
             catalog_url='http://datos.jus.gob.ar',
             indexable=True).save()

    def test_invalid_read_datajson(self):
        stderr = StringIO()
        call_command('read_datajson', stderr=stderr)
        self.assertTrue(stderr.getvalue())
