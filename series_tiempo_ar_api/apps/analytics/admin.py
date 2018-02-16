# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from series_tiempo_ar_api.apps.analytics.models import Query
from .tasks import export


class QueryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'params',)
    readonly_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')

    search_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')
    actions = ('export_analytics', )

    def export_analytics(self, *_):
        export.delay()
    export_analytics.short_description = "Export analytics"


admin.site.register(Query, QueryAdmin)
