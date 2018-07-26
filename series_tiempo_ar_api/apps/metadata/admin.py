# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import IndexMetadataTask, CatalogAlias
from .indexer.metadata_indexer import run_metadata_indexer
from django.contrib import messages


class IndexMetadataTaskAdmin(admin.ModelAdmin):
    readonly_fields = ('status', 'created', 'finished', 'logs',)
    list_display = ('__unicode__', 'status')

    task = run_metadata_indexer

    def save_model(self, request, obj, form, change):
        super(IndexMetadataTaskAdmin, self).save_model(request, obj, form, change)
        self.task.delay(obj)  # Ejecuta indexación

    def add_view(self, request, form_url='', extra_context=None):
        if not IndexMetadataTask.objects.filter(status=IndexMetadataTask.RUNNING):
            return super(IndexMetadataTaskAdmin, self).add_view(request, form_url, extra_context)
        else:
            messages.error(request, "Ya está corriendo una indexación")
            return super(IndexMetadataTaskAdmin, self).changelist_view(request, None)


@admin.register(CatalogAlias)
class CatalogAliasAdmin(admin.ModelAdmin):
    list_display = ('alias', 'ids')

    def ids(self, obj: CatalogAlias):
        return ', '.join(obj.resolve()) or None
    ids.short_description = 'catalog_ids'


admin.site.register(IndexMetadataTask, IndexMetadataTaskAdmin)
