# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .bulk_index import bulk_index
from .models import DatasetIndexingFile, Node


class DatasetsIndexingFileAdmin(admin.ModelAdmin):
    actions = ['bulk_index_datasets']

    readonly_fields = ('created', 'modified', 'state', 'logs')

    def bulk_index_datasets(self, _, queryset):
        for model in queryset:
            model.state = DatasetIndexingFile.state = DatasetIndexingFile.PROCESSING
            model.logs = u'-'  # Valor default mientras se ejecuta
            model.save()
            bulk_index.delay(model.id)
    bulk_index_datasets.short_description = 'Ejecutar'

    def get_form(self, request, obj=None, **kwargs):
        form = super(DatasetsIndexingFileAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['uploader'].initial = request.user
        return form

    def save_form(self, request, form, change):
        return super(DatasetsIndexingFileAdmin, self).save_form(request, form, change)


class NodeAdmin(admin.ModelAdmin):

    list_display = ('catalog_id', 'indexable')
    actions =  ('make_indexable', 'make_unindexable')

    def make_unindexable(self, _, queryset):
        queryset.update(indexable=False)
    make_unindexable.short_description = 'Marcar como no indexable'

    def make_indexable(self, _, queryset):
        queryset.update(indexable=True)
    make_indexable.short_description = 'Marcar como indexable'


admin.site.register(DatasetIndexingFile, DatasetsIndexingFileAdmin)
admin.site.register(Node, NodeAdmin)