#!coding=utf8
import os
import json

import unicodecsv
from StringIO import StringIO
from django.test import TestCase

from django.core.management import call_command
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import Node
from series_tiempo_ar_api.apps.api.models import Catalog, Dataset, Distribution, Field
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

    def test_dataset(self):
        out = attachments.generate_dataset_attachment()

        stream = StringIO(out)
        reader = unicodecsv.reader(stream)
        reader.next()  # Skip header

        for row in reader:
            dataset = Dataset.objects.get(identifier=row[0])

            self.assertEqual(str(dataset.indexable), row[4])
            self.assertEqual(str(dataset.available), row[5])
            error = bool(dataset.error)
            self.assertEqual(str(error), row[6])

    def test_distribution(self):
        out = attachments.generate_distribution_attachment()

        stream = StringIO(out)
        reader = unicodecsv.reader(stream)
        reader.next()  # Skip header

        for row in reader:
            distribution = Distribution.objects.get(identifier=row[0])

            self.assertEqual(str(distribution.indexable), row[4])
            self.assertEqual(str(distribution.dataset.available), row[5])
            error = bool(distribution.error)
            self.assertEqual(str(error), row[6])

    def test_fields(self):

        out = attachments.generate_field_attachment()

        stream = StringIO(out)
        reader = unicodecsv.reader(stream)
        reader.next()  # Skip header

        fields = Field.objects.all()
        for row in reader:
            field = fields.get(series_id=row[0])

            self.assertEqual(str(field.distribution.dataset.indexable), row[4])
            self.assertEqual(str(field.distribution.dataset.available), row[5])
            error = bool(field.distribution.error)
            self.assertEqual(str(error), row[6])
