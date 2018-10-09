#!coding=utf8
from django.contrib import admin

from series_tiempo_ar_api.apps.dump.tasks import enqueue_csv_dump_task, enqueue_xlsx_dump_task
from .models import GenerateDumpTask


class GenerateDumpTaskAdmin(admin.ModelAdmin):
    readonly_fields = ('status', 'created', 'finished', 'logs')

    def save_model(self, request, obj: GenerateDumpTask, form, change):
        super(GenerateDumpTaskAdmin, self).save_model(request, obj, form, change)
        task = {
            GenerateDumpTask.TYPE_CSV: enqueue_csv_dump_task,
            GenerateDumpTask.TYPE_XLSX: enqueue_xlsx_dump_task,
        }

        task[obj.file_type](obj.id)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('file_type',)
        else:
            return self.readonly_fields


admin.site.register(GenerateDumpTask, GenerateDumpTaskAdmin)
