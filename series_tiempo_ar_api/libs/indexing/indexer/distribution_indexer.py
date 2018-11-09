#! coding: utf-8
import json
import logging
from functools import reduce

import pandas as pd
from django.conf import settings
from django_datajsonar.models import Distribution
from elasticsearch.helpers import parallel_bulk
from series_tiempo_ar.helpers import freq_iso_to_pandas
from series_tiempo_ar_api.apps.management import meta_keys

from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.libs.indexing import constants
from series_tiempo_ar_api.libs.indexing import strings
from series_tiempo_ar_api.libs.indexing.indexer.utils import remove_duplicated_fields
from series_tiempo_ar_api.utils.csv_reader import read_distribution_csv
from .operations import process_column
from .metadata import update_enhanced_meta
from .index import tseries_index

logger = logging.getLogger(__name__)


class DistributionIndexer:
    def __init__(self, index: str):
        self.elastic = ElasticInstance.get()
        self.index_name = index
        self.index = tseries_index(index)

    def run(self, distribution):
        fields = distribution.field_set.all()
        fields = {field.title: field.identifier for field in fields}
        df = self.init_df(distribution, fields)

        # Aplica la operación de procesamiento e indexado a cada columna
        result = [process_column(df[col], self.index_name) for col in df.columns]

        if not result:  # Distribución sin series cargadas
            return

        # List flatten: si el resultado son múltiples listas las junto en una sola
        actions = reduce(lambda x, y: x + y, result) if isinstance(result[0], list) else result

        self.add_catalog_keyword(actions, distribution)
        for success, info in parallel_bulk(self.elastic, actions):
            if not success:
                logger.warning(strings.BULK_REQUEST_ERROR, info)

        remove_duplicated_fields(distribution)
        for field in distribution.field_set.exclude(title='indice_tiempo'):
            field.enhanced_meta.update_or_create(key=meta_keys.AVAILABLE, value='true')

        # Cálculo de metadatos adicionales sobre cada serie
        df.apply(update_enhanced_meta, args=(distribution.dataset.catalog.identifier, distribution.identifier))

    def init_df(self, distribution, fields):
        """Inicializa el DataFrame del CSV de la distribución pasada,
        seteando el índice de tiempo correcto y validando las columnas
        dentro de los datos

        Args:
            distribution (Distribution): modelo de distribución válido
            fields (dict): diccionario con estructura titulo: serie_id
        """

        df = read_distribution_csv(distribution)

        # Borro las columnas que no figuren en los metadatos
        for column in df.columns:
            if column not in fields:
                df.drop(column, axis='columns', inplace=True)
        columns = [fields[name] for name in df.columns]

        data = df.values
        freq = freq_iso_to_pandas(get_time_index_periodicity(distribution, fields))
        new_index = pd.date_range(df.index[0], df.index[-1], freq=freq)

        # Chequeo de series de días hábiles (business days)
        if freq == constants.DAILY_FREQ and new_index.size > df.index.size:
            new_index = pd.date_range(df.index[0],
                                      df.index[-1],
                                      freq=constants.BUSINESS_DAILY_FREQ)

        return pd.DataFrame(index=new_index, data=data, columns=columns)

    def add_catalog_keyword(self, actions, distribution):
        for action in actions:
            action['_source']['catalog'] = distribution.dataset.catalog.identifier


def get_time_index_periodicity(distribution, fields):
    time_index = distribution.field_set.get(identifier=fields['indice_tiempo'])
    fields.pop('indice_tiempo')
    periodicity = json.loads(time_index.metadata)['specialTypeDetail']
    distribution.enhanced_meta.update_or_create(key=meta_keys.PERIODICITY, value=periodicity)
    return periodicity
