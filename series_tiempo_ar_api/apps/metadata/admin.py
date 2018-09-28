# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages
from django_datajsonar.admin import FieldAdmin, DistributionAdmin
from django_datajsonar.models import Field, Distribution

from .models import IndexMetadataTask, CatalogAlias, Synonym
from .indexer.metadata_indexer import run_metadata_indexer
from .utils import delete_metadata


@admin.register(IndexMetadataTask)
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


@admin.register(Synonym)
class SynonymAdmin(admin.ModelAdmin):
    list_display = ('terms', )


admin.site.unregister(Field)


@admin.register(Field)
class CustomFieldAdmin(FieldAdmin):
    actions = ('delete_model',)

    def get_actions(self, request):
        # Borro la acción de borrado default
        actions = super(CustomFieldAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_model(self, _, queryset):
        delete_metadata(list(queryset))
        queryset.delete()


admin.site.unregister(Distribution)


@admin.register(Distribution)
class CustomDistributionAdmin(DistributionAdmin):
    actions = ('delete_model',)

    def get_actions(self, request):
        # Borro la acción de borrado default
        actions = super(CustomDistributionAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_model(self, _, queryset):
        fields = Field.objects.filter(distribution__identifier__in=queryset.values_list('identifier', flat=True))
        delete_metadata(list(fields))
        queryset.delete()
