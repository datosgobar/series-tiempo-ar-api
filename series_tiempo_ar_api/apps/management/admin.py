# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django_datajsonar.admin.tasks import AbstractTaskAdmin
from scheduler.admin import RepeatableJobAdmin
from scheduler.models import RepeatableJob

from series_tiempo_ar_api.libs.singleton_admin import SingletonAdmin
from .tasks.indexation import read_datajson
from .tasks.integration_test import run_integration
from .models import IndexDataTask, IntegrationTestTask, IntegrationTestConfig, APIIndexingConfig


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


class DataJsonAdmin(AbstractTaskAdmin):
    task = read_datajson

    model = IndexDataTask

    callable_str = 'series_tiempo_ar_api.apps.management.tasks.indexation.schedule_api_indexing'


@admin.register(IntegrationTestTask)
class IntegrationTestTaskAdmin(AbstractTaskAdmin):
    model = IntegrationTestTask

    task = run_integration

    callable_str = 'series_tiempo_ar_api.apps.management.tasks.integration_test.run_integration'


admin.site.register(IndexDataTask, DataJsonAdmin)
admin.site.register(IntegrationTestConfig, SingletonAdmin)
admin.site.unregister(RepeatableJob)
admin.site.register(RepeatableJob, RepeatableJobAdmin)
admin.site.register(APIIndexingConfig, SingletonAdmin)

admin.site.login_template = 'login.html'
