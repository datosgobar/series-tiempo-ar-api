#! coding: utf-8
from __future__ import division

import json

from pydatajson import DataJson

from django_datajsonar.models import Distribution
from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.libs.indexing.tasks import index_distribution
from .strings import READ_ERROR


def index_catalog(node, task, read_local=False):
    """Ejecuta el pipeline de lectura, guardado e indexado de datos
    y metadatos sobre cada distribución del catálogo especificado

    Args:
        node (Node): Nodo a indexar
        task (ReadDataJsonTask): Task a loggear acciones
        read_local (bool): Lee las rutas a archivos fuente como archivo
        local o como URL. Default False
    """

    try:
        catalog = DataJson(node.catalog_url)
        node.catalog = json.dumps(catalog)
        node.save()
    except Exception as e:
        ReadDataJsonTask.info(task, READ_ERROR.format(node.catalog_id, e))
        return

    for distribution in Distribution.objects.filter(present=True, dataset__catalog__identifier=node.catalog_id):
        index_distribution.delay(distribution.identifier, node.id, task.id, read_local)
