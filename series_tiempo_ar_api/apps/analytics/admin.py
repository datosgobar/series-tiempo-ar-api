# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from series_tiempo_ar_api.apps.analytics.models import Query


class QueryAdmin(ModelAdmin):
    list_display = ('timestamp', 'params',)
    readonly_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')
    search_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')


admin.site.register(Query, QueryAdmin)
