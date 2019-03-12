#! coding: utf-8
import json
import logging
from functools import reduce

import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from series_tiempo_ar.helpers import freq_iso_to_pandas
from django_datajsonar.models import Distribution, Field

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.field_utils import get_distribution_time_index, SeriesRepository
from series_tiempo_ar_api.libs.indexing import constants
from series_tiempo_ar_api.libs.indexing import strings

from .operations import process_column
from .metadata import update_enhanced_meta
from .index import tseries_index

logger = logging.getLogger(__name__)


class DistributionIndexer:
    def __init__(self, index: str):
        self.elastic: Elasticsearch = connections.get_connection()
        self.index_name = index
        self.index = tseries_index(index)

    def run(self, distribution):
        time_index = get_distribution_time_index(distribution)
        df = self.init_df(distribution, time_index)

        actions = self.generate_es_actions(df, distribution)

        if not actions:
            return

        for success, info in parallel_bulk(self.elastic, actions):
            if not success:
                logger.warning(strings.BULK_REQUEST_ERROR, info)

        self.update_distribution_metadata(distribution, time_index)
        df.apply(update_enhanced_meta, args=(distribution.dataset.catalog.identifier, distribution.identifier))

    def generate_es_actions(self, df, distribution):
        es_actions = [process_column(df[col], self.index_name) for col in df.columns]

        # List flatten: si el resultado son múltiples listas las junto en una sola
        actions = reduce(lambda x, y: x + y, es_actions) if isinstance(es_actions[0], list) else es_actions
        self.add_catalog_keyword(actions, distribution)
        return actions

    def update_distribution_metadata(self, distribution, time_index):
        for field in SeriesRepository.get_present_series(distribution=distribution).exclude(id=time_index.id):
            field.enhanced_meta.update_or_create(key=meta_keys.AVAILABLE, value='true')
        # Cálculo de metadatos adicionales sobre cada serie
        distribution.enhanced_meta.update_or_create(key=meta_keys.PERIODICITY,
                                                    defaults={
                                                        'value': get_distribution_time_index_periodicity(time_index)})

    def init_df(self, distribution: Distribution, time_index: Field):
        """Inicializa el DataFrame del CSV de la distribución pasada,
        seteando el índice de tiempo correcto y validando las columnas
        dentro de los datos
        """
        df = read_distribution_csv_as_df(distribution, time_index)
        fields = SeriesRepository.get_present_series(distribution=distribution)
        drop_null_or_missing_fields_from_df(df, [field.title for field in fields])

        data = df.values
        new_index = generate_df_time_index(df, time_index)
        identifiers = get_distribution_series_identifers(distribution, series_titles=df.columns)
        return pd.DataFrame(index=new_index, data=data, columns=identifiers)

    def add_catalog_keyword(self, actions, distribution):
        for action in actions:
            action['_source']['catalog'] = distribution.dataset.catalog.identifier

    def reindex(self, distribution: Distribution):
        self._delete_distribution_data(distribution)
        self.run(distribution)

    def _delete_distribution_data(self, distribution):
        fields_to_delete = list(
            SeriesRepository.get_present_series(distribution=distribution)
            .exclude(identifier=None)
            .values_list('identifier', flat=True)
        )
        series_data = Search(using=self.elastic, index=self.index._name).filter('terms', series_id=fields_to_delete)
        series_data.delete()


def read_distribution_csv_as_df(distribution: Distribution, time_index: Field) -> pd.DataFrame:
    df = pd.read_csv(distribution.data_file,
                     parse_dates=[time_index.title],
                     index_col=time_index.title)
    return df


def drop_null_or_missing_fields_from_df(df, field_titles):
    for column in df.columns:
        all_null = df[column].isnull().all()
        if all_null or column not in field_titles:
            df.drop(column, axis='columns', inplace=True)


def get_distribution_time_index_periodicity(time_index: Field) -> str:
    periodicity = json.loads(time_index.metadata)[constants.SPECIAL_TYPE_DETAIL]
    return periodicity


def generate_df_time_index(df: pd.DataFrame, time_index: Field):
    periodicity = get_distribution_time_index_periodicity(time_index)
    freq = freq_iso_to_pandas(periodicity)
    new_index = pd.date_range(df.index[0], df.index[-1], freq=freq)

    # Chequeo de series de días hábiles (business days)
    if freq == constants.DAILY_FREQ and new_index.size > df.index.size:
        new_index = pd.date_range(df.index[0],
                                  df.index[-1],
                                  freq=constants.BUSINESS_DAILY_FREQ)
    return new_index


def get_distribution_series_identifers(distribution: Distribution, series_titles: list) -> list:
    identifier_for_each_title = {s.title: s.identifier
                                 for s in SeriesRepository.get_present_series(distribution=distribution)}
    return [identifier_for_each_title[title] for title in series_titles]
