#! coding: utf-8
from __future__ import division
import logging

from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.indexing.database_loader import \
    DatabaseLoader
from series_tiempo_ar_api.apps.api.indexing.indexer import Indexer
from series_tiempo_ar_api.apps.api.indexing.scraping import get_scraper


logger = logging.Logger(__name__)
logger.addHandler(logging.StreamHandler())


class ReaderPipeline(object):
    def __init__(self, catalog, index_only=False):
        """Ejecuta el pipeline de lectura, guardado e indexado de datos
        y metadatos sobre el catálogo especificado

        Args:
            catalog (DataJson): DataJson del catálogo a parsear
            index_only (bool): Correr sólo la indexación o no
        """

        self.catalog = catalog
        self.index_only = index_only
        self.run()

    def run(self):
        distribution_models = None
        if not self.index_only:
            scraper = get_scraper()
            scraper.run(self.catalog)
            distributions = scraper.distributions
            loader = DatabaseLoader()
            loader.run(self.catalog, distributions)
            distribution_models = loader.distribution_models
        Indexer().run(distribution_models)
