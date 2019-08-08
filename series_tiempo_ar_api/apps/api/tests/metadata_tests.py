#! coding: utf-8
import json

import faker
from django.test import TestCase
from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.api.tests.helpers import get_series_id, setup_database
from series_tiempo_ar_api.apps.api.query.metadata_response import MetadataResponse
from series_tiempo_ar_api.apps.metadata.models import SeriesUnits


class MetadataResponseTests(TestCase):
    single_series = get_series_id('month')
    faker = faker.Faker()

    def setUp(self):
        if not Field.objects.filter(identifier=self.single_series):
            setup_database()
        self.units = self.faker.pystr()
        self.field = Field.objects.get(identifier=self.single_series)
        self.field.metadata = json.dumps({'units': self.units})
        self.field.save()

    def test_theme_labels(self):
        meta = json.loads(self.field.distribution.dataset.metadata)
        meta.update({'theme': ['theme_id']})
        self.field.distribution.dataset.metadata = json.dumps(meta)
        self.field.distribution.dataset.themes = json.dumps([{'id': 'theme_id', 'label': 'test_label'}])
        self.field.distribution.dataset.save()

        full_meta = MetadataResponse(self.field, simple=False, flat=False).get_response()

        self.assertTrue(isinstance(full_meta['dataset']['theme'], list))
        self.assertEqual(full_meta['dataset']['theme'][0]['label'], 'test_label')
