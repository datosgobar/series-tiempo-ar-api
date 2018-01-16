#! coding: utf-8
from __future__ import division

import json
import logging

from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.indexing.database_loader import \
    DatabaseLoader
from series_tiempo_ar_api.apps.api.indexing.indexer import Indexer
from series_tiempo_ar_api.apps.api.indexing.scraping import get_scraper
from series_tiempo_ar_api.apps.api.indexing import strings
from series_tiempo_ar_api.apps.api.models import Dataset, Distribution

logger = logging.getLogger(__name__)


def index_catalog(catalog, catalog_id, read_local=False, task=None, async=True):
    """Ejecuta el pipeline de lectura, guardado e indexado de datos
    y metadatos sobre el catálogo especificado

    Args:
        catalog (DataJson): DataJson del catálogo a parsear
        catalog_id (str): ID único del catálogo a parsear
        read_local (bool): Lee las rutas a archivos fuente como archivo
        local o como URL. Default False
        task (ReadDataJsonTask): Task a loggear acciones
    """
    logger.info(strings.PIPELINE_START, catalog_id)
    scraper = get_scraper(read_local)
    scraper.run(catalog)
    distributions = scraper.distributions

    loader = DatabaseLoader(read_local)
    loader.run(catalog, catalog_id, distributions)

    # Indexo todos los datasets whitelisteados, independientemente de cuales fueron
    # scrapeados / cargados
    datasets = Dataset.objects.filter(catalog__identifier=catalog_id,
                                      present=True,
                                      indexable=True)
    distribution_models = Distribution.objects.filter(dataset__in=datasets)
    Indexer(async=async).run(distribution_models)

    if task:
        stats = loader.get_stats()
        task_stats = json.loads(task.stats)
        task_stats[catalog_id] = stats
        task.stats = json.dumps(task_stats)

        task.save()

        task.generate_email()
