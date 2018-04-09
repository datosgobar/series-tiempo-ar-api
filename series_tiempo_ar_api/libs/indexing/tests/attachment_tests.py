#!coding=utf8
import os
import json

import unicodecsv
from StringIO import StringIO
from django.test import TestCase

from django.core.management import call_command
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import Node
from series_tiempo_ar_api.apps.api.models import Catalog
from series_tiempo_ar_api.libs.indexing.report import attachments

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class AttachmentTests(TestCase):
    catalog_id = 'test_catalog'
    catalog = os.path.join(SAMPLES_DIR, 'sample_data.json')

    @classmethod
    def setUpClass(cls):
        super(AttachmentTests, cls).setUpClass()
        cls.node = Node(catalog_id=cls.catalog_id,
                        catalog_url=cls.catalog,
                        indexable=True,
                        catalog=json.dumps(DataJson(cls.catalog)))

        cls.node.save()
        call_command('read_datajson', whitelist=True)

    def test_catalog(self):
        out = attachments.generate_catalog_attachment()

        stream = StringIO(out)
        reader = unicodecsv.reader(stream)
        reader.next()  # Skip header

        catalog = Catalog.objects.first()
        row = reader.next()
        self.assertEqual(len(row), 8)
        self.assertTrue(row[0], catalog.identifier)
        self.assertTrue(row[1], catalog.title)
        self.assertTrue(row[4], str(self.node.indexable))
