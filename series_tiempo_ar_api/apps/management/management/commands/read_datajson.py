#! coding: utf-8
import logging

from django.core.management import BaseCommand
from django.utils import timezone

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.apps.management.tasks import read_datajson

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando para ejecutar la indexación manualmente de manera sincrónica,
    útil para debugging"""

    def add_arguments(self, parser):
        parser.add_argument('--no-async', action='store_true')

    def handle(self, *args, **options):
        status = [ReadDataJsonTask.INDEXING, ReadDataJsonTask.RUNNING]
        if ReadDataJsonTask.objects.filter(status__in=status):
            logger.info(u'Ya está corriendo una indexación')
            return

        async = not options['no_async']  # True by default

        task = ReadDataJsonTask()
        task.save()

        task_id = task.id
        read_datajson(task, async=async)

        if not async:
            # Se finalizó de manera sincronica
            task = ReadDataJsonTask.objects.get(id=task_id)
            task.status = task.FINISHED
            task.finished = timezone.now()
            task.save()
            task.generate_email()
