#! coding: utf-8
import json
from django.test import TestCase
from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.api.tests.helpers import get_series_id
from series_tiempo_ar_api.apps.api.query.metadata_response import MetadataResponse


class MetadataResponseTests(TestCase):
    single_series = get_series_id('month')

    def setUp(self):
        self.field = Field.objects.get(identifier=self.single_series)

    def test_theme_labels(self):
        meta = json.loads(self.field.distribution.dataset.metadata)
        meta.update({'theme': ['theme_id']})
        self.field.distribution.dataset.metadata = json.dumps(meta)
        self.field.distribution.dataset.themes = json.dumps([{'id': 'theme_id', 'label': 'test_label'}])
        self.field.distribution.dataset.save()

        full_meta = MetadataResponse(self.field, simple=False, flat=False).get_response()

        self.assertTrue(isinstance(full_meta['dataset']['theme'], list))
        self.assertEqual(full_meta['dataset']['theme'][0]['label'], 'test_label')
