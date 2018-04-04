#! coding: utf-8
from __future__ import division

import json

from django.db.models import Q
from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.models import Dataset, Catalog, Distribution, Field
from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.libs.indexing.report.indicators import IndicatorLoader
from series_tiempo_ar_api.libs.indexing.tasks import index_distribution
from .strings import READ_ERROR


def index_catalog(node, task, read_local=False, whitelist=False):
    """Ejecuta el pipeline de lectura, guardado e indexado de datos
    y metadatos sobre cada distribución del catálogo especificado

    Args:
        node (Node): Nodo a indexar
        task (ReadDataJsonTask): Task a loggear acciones
        read_local (bool): Lee las rutas a archivos fuente como archivo
        local o como URL. Default False
        whitelist (bool): Marcar los datasets nuevos como indexables por defecto. Default False
    """

    try:
        catalog = DataJson(node.catalog_url)
        node.catalog = json.dumps(catalog)
        node.save()
    except Exception as e:
        ReadDataJsonTask.info(task, READ_ERROR.format(node.catalog_id, e.message))
        return

    # Seteo inicial de variables a usar durante la indexación
    catalog_model = Catalog.objects.filter(identifier=node.catalog_id)
    if catalog_model:
        catalog_model[0].updated = False
        catalog_model[0].error = False
        catalog_model[0].save()

    Dataset.objects.filter(catalog__identifier=node.catalog_id).update(present=False, updated=False, error=False)
    # Borro de la lista de indexables a los datasets que ya no están presentes en el catálogo
    dataset_ids = [dataset['identifier'] for dataset in catalog.get_datasets()]
    Dataset.objects \
        .filter(Q(catalog__identifier=node.catalog_id) & ~Q(identifier__in=dataset_ids)) \
        .update(indexable=False)

    Distribution.objects.filter(dataset__catalog__identifier=node.catalog_id).update(updated=False)
    Field.objects.filter(distribution__dataset__catalog=catalog_model).update(updated=False)
    for distribution in catalog.get_distributions(only_time_series=True):
        identifier = distribution['identifier']
        index_distribution.delay(identifier, node.id, task.id, read_local, whitelist)
