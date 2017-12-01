#! coding: utf-8
import logging

import pandas as pd
import requests
from django.conf import settings
from pydatajson import DataJson
from series_tiempo_ar.search import get_time_series_distributions
from series_tiempo_ar.validations import validate_distribution

from .constants import IDENTIFIER, DOWNLOAD_URL, DATASET_IDENTIFIER
from series_tiempo_ar_api.apps.api.indexing import strings

logger = logging.getLogger(__name__)


class Scraper(object):
    def __init__(self, read_local=False):
        self.distributions = []
        self.read_local = read_local

    def run(self, catalog):
        """
        Valida las distribuciones de series de tiempo de un catálogo
        entero a partir de su URL, o archivo fuente
        """
        logger.info(strings.START_SCRAPING)
        catalog = DataJson(catalog)
        distributions = []
        for distribution in get_time_series_distributions(catalog):
            distribution_id = distribution[IDENTIFIER]
            if not (self.read_local or self._validate_url(distribution)):
                continue

            url = distribution[DOWNLOAD_URL]
            dataset = catalog.get_dataset(distribution[DATASET_IDENTIFIER])
            df = pd.read_csv(url, parse_dates=[settings.INDEX_COLUMN])
            df = df.set_index(settings.INDEX_COLUMN)

            try:
                validate_distribution(df,
                                      catalog,
                                      dataset,
                                      distribution)
            except ValueError as e:
                msg = u'{} {}. Razón: {}'.format(
                    strings.DESESTIMATED_DISTRIBUTION,
                    distribution_id,
                    e.message
                )
                logger.info(msg)
            else:
                distributions.append(distribution)

        self.distributions = distributions
        logger.info(strings.END_SCRAPING)

    @staticmethod
    def _validate_url(distribution):
        distribution_id = distribution[IDENTIFIER]
        url = distribution.get(DOWNLOAD_URL)
        if not url or requests.head(url).status_code != 200:
            msg = u'{} {}'.format(strings.INVALID_DISTRIBUTION_URL,
                                  distribution_id)
            logger.info(msg)
            return False
        return True


def get_scraper(read_local=False):
    return Scraper(read_local)
