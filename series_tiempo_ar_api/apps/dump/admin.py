#!coding=utf8
from django.contrib import admin
from .models import CSVDumpTask

from .tasks import enqueue_csv_dump_task


class CSVDumpAdmin(admin.ModelAdmin):
    readonly_fields = ('status', 'created', 'finished', 'logs')

    def save_model(self, request, obj, form, change):
        super(CSVDumpAdmin, self).save_model(request, obj, form, change)
        enqueue_csv_dump_task(obj)


admin.site.register(CSVDumpTask, CSVDumpAdmin)
