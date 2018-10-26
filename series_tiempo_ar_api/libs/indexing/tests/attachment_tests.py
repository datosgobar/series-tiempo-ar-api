#!coding=utf8
import os
import json

import csv
from io import StringIO
from django.test import TestCase

from django.core.management import call_command
from pydatajson import DataJson

from django_datajsonar.models import Catalog, Dataset, Distribution, Field
from django_datajsonar.models import Node
from series_tiempo_ar_api.libs.indexing.report import attachments

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class AttachmentTests(TestCase):
    catalog_id = 'test_catalog'
    catalog = os.path.join(SAMPLES_DIR, 'sample_data.json')

    @classmethod
    def setUpClass(cls):
        super(AttachmentTests, cls).setUpClass()
        Node.objects.all().delete()
        Catalog.objects.all().delete()
        cls.node = Node(catalog_id=cls.catalog_id,
                        catalog_url=cls.catalog,
                        indexable=True,
                        catalog=json.dumps(DataJson(cls.catalog)))

        cls.node.save()
        call_command('read_datajson', whitelist=True, read_local=True)

    def test_catalog(self):
        out = attachments.generate_catalog_attachment()

        stream = StringIO(out)
        reader = csv.reader(stream)
        next(reader)  # Skip header

        catalog = Catalog.objects.first()
        row = next(reader)
        self.assertEqual(len(row), 8)
        self.assertTrue(row[0], catalog.identifier)
        self.assertTrue(row[1], catalog.title)
        self.assertTrue(row[4], str(self.node.indexable))

    def test_dataset(self):
        out = attachments.generate_dataset_attachment()

        stream = StringIO(out)
        reader = csv.reader(stream)
        next(reader)  # Skip header

        for row in reader:
            dataset = Dataset.objects.get(identifier=row[0])

            self.assertEqual(str(dataset.indexable), row[4])
            self.assertEqual(str(dataset.present), row[5])
            error = bool(dataset.error)
            self.assertEqual(str(error), row[6])

    def test_distribution(self):
        out = attachments.generate_distribution_attachment()

        stream = StringIO(out)
        reader = csv.reader(stream)
        next(reader)  # Skip header

        for row in reader:
            distribution = Distribution.objects.get(identifier=row[0])

            self.assertEqual(str(distribution.dataset.indexable), row[4])
            self.assertEqual(str(distribution.present), row[5])
            error = bool(distribution.error)
            self.assertEqual(str(error), row[6])

    def test_fields(self):

        out = attachments.generate_field_attachment()

        stream = StringIO(out)
        reader = csv.reader(stream)
        next(reader)  # Skip header

        fields = Field.objects.all()
        for row in reader:
            field = fields.get(identifier=row[0])

            self.assertEqual(str(field.distribution.dataset.indexable), row[4])
            self.assertEqual(str(field.present), row[5])
            error = bool(field.distribution.error)
            self.assertEqual(str(error), row[6])
