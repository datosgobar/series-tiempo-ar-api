#! coding: utf-8
import logging

from django.conf import settings
from django_rq import job

from django_datajsonar.models import Node
from series_tiempo_ar_api.apps.management.models import IndexDataTask
from series_tiempo_ar_api.libs.indexing.catalog_reader import index_catalog
from series_tiempo_ar_api.libs.indexing.report.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


@job('api_index')
def schedule_api_indexing(node=None, force=False):
    if IndexDataTask.objects.filter(status=IndexDataTask.RUNNING):
        logger.info(u'Ya está corriendo una indexación')
        return

    indexing_mode = IndexDataTask.ALL if force else IndexDataTask.UPDATED_ONLY
    task = IndexDataTask(indexing_mode=indexing_mode)
    task.node = node
    task.save()

    read_datajson(task, force=force)

    # Si se corre el comando sincrónicamete (local/testing), generar el reporte
    if not settings.RQ_QUEUES['indexing'].get('ASYNC', True):
        task = IndexDataTask.objects.get(id=task.id)
        ReportGenerator(task).generate()


@job('api_index')
def schedule_force_api_indexing(node=None):
    schedule_api_indexing(node, force=True)


@job('api_index')
def read_datajson(task, read_local=False, force=False):
    """Tarea raíz de indexación. Itera sobre todos los nodos indexables (federados) e
    inicia la tarea de indexación sobre cada uno de ellos
    """
    node = task.node
    nodes = Node.objects.filter(indexable=True) if node is None else [node]
    task.status = task.RUNNING
    for node in nodes:
        index_catalog(node, task, read_local, force)
