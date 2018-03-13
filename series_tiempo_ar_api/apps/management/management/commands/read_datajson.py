#! coding: utf-8
import logging

from django.core.management import BaseCommand
from django.conf import settings

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.apps.management.tasks import read_datajson
from series_tiempo_ar_api.libs.indexing.report.report_generator import ReportGenerator
from series_tiempo_ar_api.libs.indexing.tasks import scheduler
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando para ejecutar la indexación manualmente de manera sincrónica,
    útil para debugging. No correr junto con el rqscheduler para asegurar
    la generación de reportes correcta."""

    def add_arguments(self, parser):
        parser.add_argument('--whitelist', action='store_true')

    def handle(self, *args, **options):
        status = [ReadDataJsonTask.INDEXING, ReadDataJsonTask.RUNNING]
        if ReadDataJsonTask.objects.filter(status__in=status):
            logger.info(u'Ya está corriendo una indexación')
            return

        task = ReadDataJsonTask()
        task.save()

        read_datajson(task, whitelist=options['whitelist'])

        # Si se corre el comando sincrónicamete (local/testing), generar el reporte
        if not settings.RQ_QUEUES['indexing'].get('ASYNC', True):
            ReportGenerator(task).generate()
