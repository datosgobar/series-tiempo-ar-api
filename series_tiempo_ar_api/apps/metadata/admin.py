# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages
from django_datajsonar.admin import AbstractTaskAdmin
from django_datajsonar.models import Field

from series_tiempo_ar_api.libs.singleton_admin import SingletonAdmin
from .models import IndexMetadataTask, CatalogAlias, Synonym, MetadataConfig
from .indexer.metadata_indexer import run_metadata_indexer


@admin.register(IndexMetadataTask)
class IndexMetadataTaskAdmin(AbstractTaskAdmin):
    model = IndexMetadataTask
    task = run_metadata_indexer
    callable_str = 'series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer.enqueue_new_index_metadata_task'


@admin.register(CatalogAlias)
class CatalogAliasAdmin(admin.ModelAdmin):
    list_display = ('alias', 'ids')

    def ids(self, obj: CatalogAlias):
        return ', '.join(obj.resolve()) or None
    ids.short_description = 'catalog_ids'


@admin.register(Synonym)
class SynonymAdmin(admin.ModelAdmin):
    list_display = ('terms', )


@admin.register(MetadataConfig)
class MetadataConfigAdmin(SingletonAdmin):
    pass
