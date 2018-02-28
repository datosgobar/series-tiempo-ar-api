#! coding: utf-8
from __future__ import division

from pydatajson import DataJson

from series_tiempo_ar_api.libs.indexing.tasks import index_distribution


def index_catalog(catalog, catalog_id, task, read_local=False, async=True, whitelist=False):
    """Ejecuta el pipeline de lectura, guardado e indexado de datos
    y metadatos sobre cada distribución del catálogo especificado

    Args:
        catalog (DataJson): DataJson del catálogo a parsear
        catalog_id (str): ID único del catálogo a parsear
        task (ReadDataJsonTask): Task a loggear acciones
        read_local (bool): Lee las rutas a archivos fuente como archivo
        local o como URL. Default False
        async (bool): Hacer las tareas de indexación asincrónicamente. Default True
        whitelist (bool): Marcar los datasets nuevos como indexables por defecto. Default False
    """

    catalog = DataJson(catalog)

    for distribution in catalog.get_distributions(only_time_series=True):
        if async:
            index_distribution.delay(distribution, catalog, catalog_id, task, read_local, async, whitelist)
        else:
            index_distribution(distribution, catalog, catalog_id, task, read_local, async, whitelist)

    task.save()
