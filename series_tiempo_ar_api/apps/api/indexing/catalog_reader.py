#! coding: utf-8
from __future__ import division
import logging

from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.indexing.database_loader import \
    DatabaseLoader
from series_tiempo_ar_api.apps.api.indexing.indexer import Indexer
from series_tiempo_ar_api.apps.api.indexing.scraping import get_scraper
from series_tiempo_ar_api.apps.api.indexing import strings

logger = logging.Logger(__name__)
logger.addHandler(logging.StreamHandler())


def index_catalog(catalog, catalog_id, read_local=False):
    """Ejecuta el pipeline de lectura, guardado e indexado de datos
    y metadatos sobre el catálogo especificado

    Args:
        catalog (DataJson): DataJson del catálogo a parsear
        catalog_id (str): ID único del catálogo a parsear
        read_local (bool): Lee las rutas a archivos fuente como archivo
        local o como URL. Default False
    """
    logger.info(strings.PIPELINE_START, catalog_id)
    scraper = get_scraper(read_local)
    scraper.run(catalog)
    distributions = scraper.distributions

    if not distributions:
        logger.info(strings.NO_SERIES_SCRAPPED)
        return

    loader = DatabaseLoader(read_local)
    loader.run(catalog, catalog_id, distributions)
    distribution_models = loader.distribution_models
    Indexer().run(distribution_models)
