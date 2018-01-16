#! coding: utf-8
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.apps.management.tasks import read_datajson


class Command(BaseCommand):
    """Comando para ejecutar la indexación manualmente de manera sincrónica,
    útil para debugging"""
    def handle(self, *args, **options):
        status = [ReadDataJsonTask.INDEXING, ReadDataJsonTask.RUNNING]
        if ReadDataJsonTask.objects.filter(status__in=status):
            self.stderr.write(u'Ya está corriendo una indexación')
            return

        task = ReadDataJsonTask()
        task.save()

        task_id = task.id
        read_datajson(task, async=False)

        # Se finalizó de manera sincronica
        task = ReadDataJsonTask.objects.get(id=task_id)
        task.status = task.FINISHED
        task.save()
