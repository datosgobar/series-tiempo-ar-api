# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from import_export import resources
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from series_tiempo_ar_api.apps.analytics.models import Query
from .tasks import export


class QueryResource(resources.ModelResource):
    class Meta:
        model = Query
        fields = export_order = (
            'timestamp',
            'ip_address',
            'ids',
            'params',
        )


class QueryAdmin(ImportExportModelAdmin):
    list_display = ('timestamp', 'params',)
    readonly_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')

    search_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')
    resource_class = QueryResource
    actions = ('export_analytics', )

    def export_analytics(self, *_):
        export.delay()
    export_analytics.short_description = "Export analytics"


admin.site.register(Query, QueryAdmin)
