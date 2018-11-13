#!coding=utf8
from django.contrib import admin, messages

from django_datajsonar.admin import AbstractTaskAdmin

from series_tiempo_ar_api.apps.dump.tasks import enqueue_dump_task
from .models import GenerateDumpTask


class GenerateDumpTaskAdmin(AbstractTaskAdmin):
    model = GenerateDumpTask

    list_display = ('__str__', 'file_type', 'status')

    task = enqueue_dump_task

    def save_model(self, request, obj, form, change):
        if self.model.objects.filter(status=self.model.RUNNING, file_type=obj.file_type):
            messages.error(request, "Ya está corriendo una tarea")
            return

        super(GenerateDumpTaskAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('file_type',)
        else:
            return self.readonly_fields


admin.site.register(GenerateDumpTask, GenerateDumpTaskAdmin)
