#! coding: utf-8
from __future__ import division

import logging

import pandas as pd
import requests
from django.conf import settings
from pydatajson import DataJson
from series_tiempo_ar.search import get_time_series_distributions
from series_tiempo_ar.validations import validate_distribution

logger = logging.Logger(__name__)
logger.addHandler(logging.StreamHandler())


class Scraper(object):
    def __init__(self, read_local=False):
        self.distributions = []
        self.fields = []
        self.read_local = read_local

    def run(self, catalog):
        """Valida las distribuciones de series de tiempo de un catálogo
        entero a partir de su URL, o archivo fuente
        """
        logger.info("Comienzo del scraping")
        catalog = DataJson(catalog)
        distributions = []
        for distribution in get_time_series_distributions(catalog):
            distribution_id = distribution['identifier']
            if not (self.read_local or self._validate_url(distribution)):
                continue

            url = distribution['downloadURL']
            dataset = catalog.get_dataset(distribution['dataset_identifier'])
            df = pd.read_csv(url, parse_dates=[settings.INDEX_COLUMN])
            df = df.set_index(settings.INDEX_COLUMN)

            try:
                validate_distribution(df,
                                      catalog,
                                      dataset,
                                      distribution)
            except ValueError as e:
                msg = u'Desestimada la distribución {}. Razón: {}'.format(
                    distribution_id,
                    e.message
                )
                logger.info(msg)
            else:
                distributions.append(distribution)

        self.distributions = distributions
        logger.info("Fin del scraping")

    @staticmethod
    def _validate_url(distribution):
        distribution_id = distribution['identifier']
        url = distribution.get('downloadURL')
        if not url or requests.head(url).status_code != 200:
            msg = u'URL inválida en distribución {}'.format(distribution_id)
            logger.info(msg)
            return False
        return True


def get_scraper():
    return Scraper()
