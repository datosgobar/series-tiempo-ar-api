#!coding=utf8
import os

from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.utils import timezone

from django_datajsonar.admin.tasks import AbstractTaskAdmin

from series_tiempo_ar_api.apps.dump.tasks import enqueue_dump_task
from .models import GenerateDumpTask, DumpFile


class GenerateDumpTaskAdmin(AbstractTaskAdmin):
    model = GenerateDumpTask

    list_display = ('__str__', 'file_type', 'status')
    actions = ['delete_model', 'mark_finished']

    task = enqueue_dump_task

    callable_str = 'series_tiempo_ar_api.apps.dump.tasks.enqueue_write_csv_task'

    def get_actions(self, request):
        actions = super(GenerateDumpTaskAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']

        return actions

    def delete_model(self, request, queryset):
        obj: GenerateDumpTask
        for obj in queryset:  # Fuerza el borrado de los archivos en el sistema
            obj.delete()

    def mark_finished(self, _, queryset: QuerySet):
        queryset.update(status=self.model.FINISHED)
        queryset.filter(finished=None).update(finished=timezone.now())

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
