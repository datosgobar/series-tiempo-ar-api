#! coding: utf-8
import logging

import numpy as np
import pandas as pd
from django.conf import settings
from elasticsearch.helpers import parallel_bulk
from series_tiempo_ar.helpers import freq_iso_to_pandas
from django_rq import job

from series_tiempo_ar_api.apps.api.common import operations
from series_tiempo_ar_api.apps.api.models import Distribution
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance
from series_tiempo_ar_api.apps.api.indexing import strings
from series_tiempo_ar_api.apps.api.indexing import constants

# Ignora divisiones por cero, no nos molesta el NaN
np.seterr(divide='ignore', invalid='ignore')

logger = logging.getLogger(__name__)


class Indexer(object):
    """Lee distribuciones y las indexa a través de un bulk create en
    Elasticsearch
    """

    def __init__(self, index=settings.TS_INDEX):
        self.elastic = ElasticInstance()
        self.index = index

    def run(self, distributions=None):
        """Indexa en Elasticsearch todos los datos de las
        distribuciones guardadas en la base de datos, o las
        especificadas por el iterable 'distributions'
        """
        self.init_index()

        logger.info(strings.INDEX_START)

        for distribution in distributions:
            index_distribution.delay(self.index, distribution.id)

        logger.info(strings.INDEX_END)

    def init_index(self):
        if not self.elastic.indices.exists(self.index):
            self.elastic.indices.create(self.index,
                                        body=constants.INDEX_CREATION_BODY)


@job('indexing')
def index_distribution(index, distribution_id):
    distribution = Distribution.objects.get(id=distribution_id)

    DistributionIndexer(index=index).run(distribution)


class DistributionIndexer:
    def __init__(self, index):
        self.elastic = ElasticInstance.get()
        self.index = index
        self.indexed_fields = set()
        self.bulk_actions = []

    def run(self, distribution):
        fields = distribution.field_set.all()
        fields = {field.title: field.series_id for field in fields}
        df = self.init_df(distribution, fields)

        # Aplica la operación de procesamiento e indexado a cada columna
        result = [operations.process_column(df[col], self.index) for col in df.columns]

        if not len(result):  # Distribución sin series cargadas
            return

        # List flatten: si el resultado son múltiples listas las junto en una sola
        actions = reduce(lambda x, y: x + y, result) if isinstance(result[0], list) else result

        for success, info in parallel_bulk(self.elastic, actions):
            if not success:
                logger.warn(strings.BULK_REQUEST_ERROR, info)

        # Fuerzo a que los datos estén disponibles para queries inmediatamente
        segments = constants.FORCE_MERGE_SEGMENTS
        self.elastic.indices.forcemerge(index=self.index,
                                        max_num_segments=segments)

    @staticmethod
    def init_df(distribution, fields):
        """Inicializa el DataFrame del CSV de la distribución pasada,
        seteando el índice de tiempo correcto y validando las columnas
        dentro de los datos

        Args:
            distribution (Distribution): modelo de distribución válido
            fields (dict): diccionario con estructura titulo: serie_id
        """

        df = pd.read_csv(distribution.data_file.file,
                         parse_dates=[settings.INDEX_COLUMN])
        df = df.set_index(settings.INDEX_COLUMN)

        # Borro las columnas que no figuren en los metadatos
        for column in df.columns:
            if column not in fields:
                df.drop(column, axis='columns', inplace=True)
        columns = [fields[name] for name in df.columns]

        data = np.array(df)
        freq = freq_iso_to_pandas(distribution.periodicity)
        new_index = pd.date_range(df.index[0], df.index[-1], freq=freq)

        # Chequeo de series de días hábiles (business days)
        if freq == constants.DAILY_FREQ and new_index.size > df.index.size:
            new_index = pd.date_range(df.index[0],
                                      df.index[-1],
                                      freq=constants.BUSINESS_DAILY_FREQ)

        return pd.DataFrame(index=new_index, data=data, columns=columns)
