#! coding: utf-8

from django.utils import timezone
from django_rq import job

from django_datajsonar.models import Node
from series_tiempo_ar_api.libs.indexing.catalog_reader import index_catalog


@job('indexing')
def read_datajson(task, whitelist=False, read_local=False):
    """Tarea raíz de indexación. Itera sobre todos los nodos indexables (federados) e
    inicia la tarea de indexación sobre cada uno de ellos
    """
    nodes = Node.objects.filter(indexable=True)
    task.status = task.RUNNING

    for node in nodes:
        index_catalog(node, task, read_local, whitelist)
