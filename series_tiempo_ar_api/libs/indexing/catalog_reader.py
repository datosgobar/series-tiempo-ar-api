#! coding: utf-8
from __future__ import division

import json

from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.models import Dataset
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
        catalog = DataJson(node.catalog_url)
        node.catalog = json.dumps(catalog)
        node.save()
    except Exception as e:
        ReadDataJsonTask.info(task, READ_ERROR.format(node.catalog_id, e.message))
        return

    Dataset.objects.filter(catalog__identifier=node.catalog_id).update(present=False)
    for distribution in catalog.get_distributions(only_time_series=True):
        identifier = distribution['identifier']
        if async:
            index_distribution.delay(identifier, node.id, task, read_local, whitelist)
        else:
            index_distribution(identifier, node.id, task, read_local, whitelist)

    task.save()
