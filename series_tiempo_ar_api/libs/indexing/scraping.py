#! coding: utf-8
import logging
import urllib

import pandas as pd
import requests
from django.conf import settings
from series_tiempo_ar.validations import validate_distribution

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.libs.indexing import strings
from .constants import IDENTIFIER, DOWNLOAD_URL, DATASET_IDENTIFIER

logger = logging.getLogger(__name__)


class Scraper(object):
    def __init__(self, task, read_local=False):
        self.task = task
        self.read_local = read_local

    def run(self, distribution, catalog):
        """
        Valida las distribuciones de series de tiempo de un catálogo
        entero a partir de su URL, o archivo fuente
        """
        distribution_id = distribution.get(IDENTIFIER)
        url = distribution.get(DOWNLOAD_URL)
        if not self.read_local:
            if not url or requests.head(url).status_code != 200:
                msg = u'{} {}'.format(strings.INVALID_DISTRIBUTION_URL,
                                      distribution_id)
                self.task.info(msg)
                return False

        # Fix a pandas fallando en lectura de URLs no ascii
        url = url.encode('UTF-8')
        url = urllib.quote(url, safe='/:')

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
            ReadDataJsonTask.info(self.task, msg)
            return False

        return True
