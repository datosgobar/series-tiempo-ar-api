# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import DatasetIndexingFile
from series_tiempo_ar_api.apps.management.tasks import bulk_index
from series_tiempo_ar_api.apps.api.models import Catalog, Dataset

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class BulkIndexingTests(TestCase):

    test_catalog = 'test'
    other_catalog = 'other'

    catalogs = (test_catalog, other_catalog)
    datasets_per_catalog = 3

    def setUp(self):
        self.user = User(username='test_user', password='test_pass', email='test@email.com')
        self.user.save()

        for catalog in self.catalogs:
            catalog_model = Catalog(identifier=catalog, title='', metadata='')
            catalog_model.save()
            for i in range(self.datasets_per_catalog):
                dataset = Dataset(identifier=i, catalog=catalog_model, metadata='')
                dataset.save()

    def test_indexing_file(self):
        filepath = os.path.join(dir_path, 'test_indexing_file.csv')

        dataset = Dataset.objects.get(catalog__identifier=self.test_catalog, identifier='1')
        self.assertFalse(dataset.indexable)

        with open(filepath, 'r') as f:
            idx_file = DatasetIndexingFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                           uploader=self.user)
            idx_file.save()

            bulk_index(idx_file.id)
        dataset = Dataset.objects.get(catalog__identifier=self.test_catalog, identifier='1')
        self.assertTrue(dataset.indexable)

    def test_dataset_not_in_file_unaffected(self):
        filepath = os.path.join(dir_path, 'test_indexing_file.csv')

        dataset = Dataset.objects.get(catalog__identifier=self.test_catalog, identifier='0')
        self.assertFalse(dataset.indexable)
        with open(filepath, 'r') as f:
            idx_file = DatasetIndexingFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                           uploader=self.user)
            idx_file.save()

            bulk_index(idx_file.id)

        dataset = Dataset.objects.get(catalog__identifier=self.test_catalog, identifier='0')
        self.assertFalse(dataset.indexable)

    def test_idx_file_model_changes_states(self):
        filepath = os.path.join(dir_path, 'test_indexing_file.csv')
        with open(filepath, 'r') as f:
            idx_file = DatasetIndexingFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                           uploader=self.user)
            idx_file.save()

            bulk_index(idx_file.id)

        idx_file = DatasetIndexingFile.objects.first()
        self.assertEqual(idx_file.state, idx_file.PROCESSED)

    def test_missing_dataset_header(self):
        filepath = os.path.join(dir_path, 'missing_dataset_headers.csv')
        with open(filepath, 'r') as f:
            idx_file = DatasetIndexingFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                           uploader=self.user)
            idx_file.save()

            bulk_index(idx_file.id)

        idx_file = DatasetIndexingFile.objects.first()
        self.assertEqual(idx_file.state, idx_file.FAILED)

    def tearDown(self):
        for catalog in self.catalogs:
            Catalog.objects.get(identifier=catalog).delete()
        self.user.delete()
