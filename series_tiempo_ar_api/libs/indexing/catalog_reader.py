#! coding: utf-8
from __future__ import division

import json

from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.libs.indexing.tasks import index_distribution
from .strings import READ_ERROR


def index_catalog(node, task, read_local=False, async=True, whitelist=False):
    """Ejecuta el pipeline de lectura, guardado e indexado de datos
    y metadatos sobre cada distribución del catálogo especificado

    Args:
        node (Node): Nodo a indexar
        task (ReadDataJsonTask): Task a loggear acciones
        read_local (bool): Lee las rutas a archivos fuente como archivo
        local o como URL. Default False
        async (bool): Hacer las tareas de indexación asincrónicamente. Default True
        whitelist (bool): Marcar los datasets nuevos como indexables por defecto. Default False
    """

    try:
        catalog = DataJson(json.loads(node.catalog))
    except Exception as e:
        ReadDataJsonTask.info(task, READ_ERROR.format(node.catalog_id, e.message))
        return

    for distribution in catalog.get_distributions(only_time_series=True):
        if async:
            index_distribution.delay(distribution, node, task, read_local, async, whitelist)
        else:
            index_distribution(distribution, node, task, read_local, async, whitelist)

    task.save()
