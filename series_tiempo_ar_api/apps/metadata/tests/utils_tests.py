# -*- coding: utf-8 -*-
from django.test import TestCase
from series_tiempo_ar_api.apps.metadata.utils import resolve_catalog_id_aliases
from series_tiempo_ar_api.apps.metadata.models import CatalogAlias

from django_datajsonar.models import Node


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
