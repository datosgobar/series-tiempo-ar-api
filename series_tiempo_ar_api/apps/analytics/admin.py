# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from series_tiempo_ar_api.apps.analytics.models import Query


class QueryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'ip_address', 'params',)
    readonly_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')

    search_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')


admin.site.register(Query, QueryAdmin)
