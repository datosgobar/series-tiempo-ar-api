# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.core.paginator import Paginator
from django.db import connection
from django_datajsonar.admin import AbstractTaskAdmin

from series_tiempo_ar_api.libs.singleton_admin import SingletonAdmin
from .models import Query, ImportConfig, AnalyticsImportTask
from .tasks import enqueue_new_import_analytics_task, import_analytics


class LargeTablePaginator(Paginator):
    """
    Source: https://medium.com/squad-engineering/estimated-counts-for-faster-django-admin-change-list-963cbf43683e
    Warning: Postgresql only hack
    Overrides the count method of QuerySet objects to get an estimate instead of actual count when not filtered.
    However, this estimate can be stale and hence not fit for situations where the count of objects actually matter.
    """

    def _get_count(self):
        if getattr(self, '_count', None) is not None:
            return self._count

        query = self.object_list.query
        if not query.where:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT reltuples FROM pg_class WHERE relname = %s",
                               [query.model._meta.db_table])
                self._count = int(cursor.fetchone()[0])
            except Exception as _:
                self._count = super(LargeTablePaginator, self).count
        else:
            self._count = super(LargeTablePaginator, self).count

        return self._count

    count = property(_get_count)


class QueryAdmin(admin.ModelAdmin):
    # Impide hacer un COUNT(*) adicional en el armado de respuesta
    show_full_result_count = False

    paginator = LargeTablePaginator

    list_display = ('timestamp', 'status_code', 'uri', 'ip_address', 'params',)

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.opts.local_fields]


class ImportConfigAdmin(SingletonAdmin):
    pass


class ImportTaskAdmin(AbstractTaskAdmin):
    task = import_analytics

    model = AnalyticsImportTask

    callable_str = 'series_tiempo_ar_api.apps.analytics.tasks.enqueue_new_import_analytics_task'


admin.site.register(Query, QueryAdmin)
admin.site.register(ImportConfig, ImportConfigAdmin)
admin.site.register(AnalyticsImportTask, ImportTaskAdmin)
