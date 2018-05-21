# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .tasks import read_datajson
from .models import IndexingTaskCron, ReadDataJsonTask, NodeAdmins


class NodeAdmin(admin.ModelAdmin):

    list_display = ('catalog_id', 'indexable')
    actions = ('delete_model', 'run_indexing', 'make_indexable', 'make_unindexable')
    exclude = ('catalog', )

    def get_actions(self, request):
        # Borro la acción de borrado default
        actions = super(NodeAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def make_unindexable(self, _, queryset):
        queryset.update(indexable=False)
    make_unindexable.short_description = 'Marcar como no indexable'

    def make_indexable(self, _, queryset):
        queryset.update(indexable=True)
    make_indexable.short_description = 'Marcar como indexable'


class IndexingTaskAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'enabled', 'weekdays_only')

    actions = ('delete_model',)

    def get_actions(self, request):
        # Borro la acción de borrado default
        actions = super(IndexingTaskAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_model(self, _, queryset):
        # Actualizo los crons del sistema para reflejar el cambio de modelos
        queryset.delete()
        IndexingTaskCron.update_crontab()


class DataJsonAdmin(admin.ModelAdmin):
    readonly_fields = ('status', 'created', 'finished', 'logs', 'stats')
    list_display = ('__unicode__', 'status')

    def save_model(self, request, obj, form, change):
        running_status = [ReadDataJsonTask.RUNNING, ReadDataJsonTask.INDEXING]
        if ReadDataJsonTask.objects.filter(status__in=running_status):
            return  # Ya hay tarea corriendo, no ejecuto una nueva
        super(DataJsonAdmin, self).save_model(request, obj, form, change)
        read_datajson.delay(obj)  # Ejecuta indexación


admin.site.register(NodeAdmins)
admin.site.register(IndexingTaskCron, IndexingTaskAdmin)
admin.site.register(ReadDataJsonTask, DataJsonAdmin)
