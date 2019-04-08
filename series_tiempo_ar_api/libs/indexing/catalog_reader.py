#! coding: utf-8
from __future__ import division

import json

from pydatajson import DataJson

from django_datajsonar.models import Distribution
from series_tiempo_ar_api.apps.management.models import IndexDataTask
from series_tiempo_ar_api.libs.indexing.tasks import index_distribution
from .strings import READ_ERROR


def index_catalog(node, task, read_local=False, force=False):
    """Ejecuta el pipeline de lectura, guardado e indexado de datos
    y metadatos sobre cada distribución del catálogo especificado
    """

    try:
        catalog = DataJson(node.catalog_url)
        node.catalog = json.dumps(catalog)
        node.save()
    except Exception as e:
        IndexDataTask.info(task, READ_ERROR.format(node.catalog_id, e))
        return

    distributions = Distribution.objects.filter(present=True,
                                                dataset__indexable=True,
                                                dataset__catalog__identifier=node.catalog_id)
    for distribution in distributions:
        index_distribution.delay(distribution.identifier, node.id, task.id, read_local, force=force)
