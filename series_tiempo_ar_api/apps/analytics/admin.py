# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from series_tiempo_ar_api.apps.analytics.models import Query, ImportConfig
from solo.admin import SingletonModelAdmin


class QueryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'ip_address', 'params',)
    readonly_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')

    search_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')


class ImportConfigAdmin(SingletonModelAdmin):
    # django-des overridea el change_form_template de la clase padre(!), volvemos al default de django
    change_form_template = 'admin/change_form.html'


admin.site.register(Query, QueryAdmin)
admin.site.register(ImportConfig, ImportConfigAdmin)
