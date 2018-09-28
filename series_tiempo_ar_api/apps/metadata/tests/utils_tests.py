# -*- coding: utf-8 -*-
import os

from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import User
from django.core import urlresolvers
from django.test import TestCase
from django_datajsonar.indexing.catalog_reader import index_catalog
from mock import mock

from series_tiempo_ar_api.apps.metadata.utils import resolve_catalog_id_aliases, delete_metadata
from series_tiempo_ar_api.apps.metadata.models import CatalogAlias

from django_datajsonar.models import Node, Field, ReadDataJsonTask, Distribution

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class ResolveAliasTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(ResolveAliasTests, cls).setUpClass()
        Node.objects.create(catalog_url='http://example.com/1', catalog_id='one_catalog', indexable=True)
        Node.objects.create(catalog_url='http://example.com/2', catalog_id='two_catalog', indexable=False)

        alias = CatalogAlias.objects.create(alias='alias_id')
        alias.nodes.add(Node.objects.first())
        alias.nodes.add(Node.objects.last())

    def test_expand(self):
        ids = resolve_catalog_id_aliases(['alias_id'])

        expected = list(Node.objects.values_list('catalog_id', flat=True))
        self.assertEqual(set(ids), set(expected))

    def test_node_not_alias_returns_unchanged(self):
        ids = resolve_catalog_id_aliases(['one_catalog'])

        expected = ['one_catalog']
        self.assertListEqual(ids, expected)

    def test_empty_list_returns_unchanged(self):
        self.assertListEqual(resolve_catalog_id_aliases([]), [])

    def test_one_alias_one_catalog_id(self):
        Node.objects.create(catalog_url='http://example.com/3', catalog_id='third_catalog', indexable=True)

        ids = resolve_catalog_id_aliases(['alias_id', 'third_catalog'])

        expected = ['one_catalog', 'two_catalog', 'third_catalog']
        self.assertEqual(set(expected), set(ids))


class DeleteMetadataTests(TestCase):
    distribution_change = urlresolvers.reverse('admin:django_datajsonar_distribution_changelist')
    field_change = urlresolvers.reverse('admin:django_datajsonar_field_changelist')

    def setUp(self):
        node = Node.objects.create(catalog_url=os.path.join(SAMPLES_DIR, 'single_distribution.json'), catalog_id="one", indexable=True)
        index_catalog(node, ReadDataJsonTask.objects.create(), whitelist=True)
        user = User.objects.create(username='a', password='b', is_staff=True, is_superuser=True)
        self.client.force_login(user)

    def test_delete_fields(self):
        with mock.patch('series_tiempo_ar_api.apps.metadata.admin.delete_metadata') as fake_delete:
            fields = Field.objects.all()
            self.client.post(self.field_change, {'action': 'delete_model',
                                                 ACTION_CHECKBOX_NAME: [str(f.pk) for f in fields]},
                             follow=True)

            self.assertEqual(set(fake_delete.call_args[0][0]), set(fields))

    def test_delete_distribution(self):
        with mock.patch('series_tiempo_ar_api.apps.metadata.admin.delete_metadata') as fake_delete:
            distribution: Distribution = Distribution.objects.first()
            fields = set(distribution.field_set.all())
            self.client.post(self.distribution_change,
                             {'action': 'delete_model',
                              ACTION_CHECKBOX_NAME: [str(distribution.pk)]},
                             follow=True)
            self.assertEqual(set(fake_delete.call_args[0][0]), set(fields))
