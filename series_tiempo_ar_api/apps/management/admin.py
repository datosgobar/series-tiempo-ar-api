# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import yaml
from django.contrib import admin
from .bulk_index import bulk_index
from .models import DatasetIndexingFile, NodeRegisterFile, Node


class BaseRegisterFileAdmin(admin.ModelAdmin):
    actions = ['run']

    readonly_fields = ('created', 'modified', 'state', 'logs')

    def run(self, _, queryset):
        raise NotImplementedError
    run.short_description = 'Ejecutar'

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseRegisterFileAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['uploader'].initial = request.user
        return form

    def save_form(self, request, form, change):
        return super(BaseRegisterFileAdmin, self).save_form(request, form, change)


class DatasetIndexingFileAdmin(BaseRegisterFileAdmin):
    def run(self, _, queryset):
        for model in queryset:
            model.state = DatasetIndexingFile.state = DatasetIndexingFile.PROCESSING
            model.logs = u'-'  # Valor default mientras se ejecuta
            model.save()
            bulk_index.delay(model.id)
    run.short_description = 'Ejecutar'


class NodeRegisterFileAdmin(BaseRegisterFileAdmin):
    def run(self, _, queryset):
        for model in queryset:
            model.state = NodeRegisterFile.state = NodeRegisterFile.PROCESSING
            model.logs = u'-'
            model.save()
            process_node_register_file(model)


def process_node_register_file(model):
    indexing_file = model.indexing_file
    yml = indexing_file.read()
    nodes = yaml.load(yml)
    for node, values in nodes.items():
        if bool(values['federado']) is True and values.get('formato') == 'json':
            node_model, _ = Node.objects.get_or_create(catalog_id=node,
                                                       catalog_url=values['url'],
                                                       indexable=True)
            node_model.save()

    model.status = NodeRegisterFile.PROCESSED


class NodeAdmin(admin.ModelAdmin):

    list_display = ('catalog_id', 'indexable')
    actions = ('delete_model', 'run_indexing', 'make_indexable', 'make_unindexable')

    def get_actions(self, request):
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

    def delete_model(self, _, queryset):
        for node in queryset:
            if node.indexable:
                for register_file in NodeRegisterFile.objects.all():
                    indexing_file = register_file.indexing_file
                    yml = indexing_file.read()
                    nodes = yaml.load(yml)
                    if node.catalog_id not in nodes or not nodes[node.catalog_id].get('federado'):
                        node.delete()
                        break


admin.site.register(DatasetIndexingFile, DatasetIndexingFileAdmin)
admin.site.register(NodeRegisterFile, NodeRegisterFileAdmin)
admin.site.register(Node, NodeAdmin)
