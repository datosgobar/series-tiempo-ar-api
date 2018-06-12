# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Query, ImportConfig, AnalyticsImportTask
from .tasks import import_last_day_analytics_from_api_mgmt


class QueryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'ip_address', 'params',)
    readonly_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')

    search_fields = ('timestamp', 'params', 'ip_address', 'args', 'ids')


class ImportConfigAdmin(SingletonModelAdmin):
    # django-des overridea el change_form_template de la clase padre(!), volvemos al default de django
    change_form_template = 'admin/change_form.html'


class ImportTaskAdmin(admin.ModelAdmin):
    readonly_fields = ('status', 'logs', 'timestamp')

    def save_model(self, request, obj, form, change):
        import_last_day_analytics_from_api_mgmt.delay()


admin.site.register(Query, QueryAdmin)
admin.site.register(ImportConfig, ImportConfigAdmin)
admin.site.register(AnalyticsImportTask, ImportTaskAdmin)
