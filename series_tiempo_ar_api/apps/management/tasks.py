#! coding: utf-8
import logging

from django.conf import settings
from django_rq import job

from django_datajsonar.models import Node
from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.libs.indexing.catalog_reader import index_catalog
from series_tiempo_ar_api.libs.indexing.report.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


def schedule_api_indexing(force=False):
    status = [ReadDataJsonTask.INDEXING, ReadDataJsonTask.RUNNING]
    if ReadDataJsonTask.objects.filter(status__in=status):
        logger.info(u'Ya está corriendo una indexación')
        return

    task = ReadDataJsonTask()
    task.save()

    read_datajson(task, force=force)

    # Si se corre el comando sincrónicamete (local/testing), generar el reporte
    if not settings.RQ_QUEUES['indexing'].get('ASYNC', True):
        task = ReadDataJsonTask.objects.get(id=task.id)
        ReportGenerator(task).generate()


@job('indexing')
def read_datajson(task, read_local=False, force=False):
    """Tarea raíz de indexación. Itera sobre todos los nodos indexables (federados) e
    inicia la tarea de indexación sobre cada uno de ellos
    """
    nodes = Node.objects.filter(indexable=True)
    task.status = task.RUNNING

    for node in nodes:
        index_catalog(node, task, read_local, force)
