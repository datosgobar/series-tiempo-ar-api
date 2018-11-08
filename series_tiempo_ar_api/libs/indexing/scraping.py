#! coding: utf-8
import logging
import urllib.parse
from io import BytesIO

import requests
import pandas as pd
from django.conf import settings
from django_datajsonar.models import Distribution
from pydatajson import DataJson
from series_tiempo_ar.validations import validate_distribution
from .strings import NO_DISTRIBUTION_URL, NO_DATASET_IDENTIFIER

logger = logging.getLogger(__name__)


class Scraper(object):
    def __init__(self, read_local=False):
        self.read_local = read_local

    def run(self, distribution_model: Distribution, catalog: DataJson):
        """
        Valida las distribuciones de series de tiempo de un catálogo
        entero a partir de su URL, o archivo fuente

        Returns:
            bool: True si la distribución pasa las validaciones, False caso contrario
        """

        url = distribution_model.download_url
        if url is None:
            raise ValueError(NO_DISTRIBUTION_URL.format(distribution_model.identifier))

        # Fix a pandas fallando en lectura de URLs no ascii
        url = url.encode('UTF-8')
        url = urllib.parse.quote(url, safe='/:?=&')

        dataset_id = distribution_model.dataset.identifier
        if dataset_id is None:
            raise ValueError(NO_DATASET_IDENTIFIER.format(distribution_model.identifier))

        dataset = catalog.get_dataset(dataset_id)
        distribution = catalog.get_distribution(distribution_model.identifier)

        df = self.init_df(url)

        validate_distribution(df, catalog, dataset, distribution)

        return True

    def init_df(self, url):
        """Wrapper de descarga de una distribución y carga en un pandas dataframe.
        No le pasamos la url a read_csv directamente para evitar problemas de
        verificación de certificados SSL
        """
        if self.read_local:
            csv = url
        else:
            csv = BytesIO(requests.get(url, verify=False).content)
        return pd.read_csv(csv,
                           parse_dates=[settings.INDEX_COLUMN],
                           index_col=settings.INDEX_COLUMN)
