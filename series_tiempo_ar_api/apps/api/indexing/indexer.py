#! coding: utf-8
import logging

import numpy as np
import pandas as pd
from django.conf import settings
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl import Search
from series_tiempo_ar.helpers import freq_iso_to_pandas

from series_tiempo_ar_api.apps.api.helpers import freq_pandas_to_interval
from series_tiempo_ar_api.apps.api.models import Distribution, Field
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance
from series_tiempo_ar_api.apps.api.common.operations import pct_change_a_year_ago, change_a_year_ago
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
            DistributionIndexer(index=self.index).run(distribution)

        # Fuerzo a que los datos estén disponibles para queries inmediatamente
        segments = constants.FORCE_MERGE_SEGMENTS
        self.elastic.indices.forcemerge(index=self.index,
                                        max_num_segments=segments)

        logger.info(strings.INDEX_END)

    def init_index(self):
        if not self.elastic.indices.exists(self.index):
            self.elastic.indices.create(self.index,
                                        body=constants.INDEX_CREATION_BODY)


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

        self.generate_properties(df, fields)

        for success, info in parallel_bulk(self.elastic, self.bulk_actions):
            if not success:
                logger.warn(strings.BULK_REQUEST_ERROR, info)

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

    def generate_properties(self, df, fields):
        df.apply(self.process_column)

        # Manejo de series faltantes
        for series_id in fields.values():
            if series_id not in self.indexed_fields:
                logger.info(strings.SERIES_NOT_FOUND, series_id)
                self._handle_missing_series(series_id)

    def process_column(self, col):
        """Procesa una columna del DataFrame: calcula los valores de
        diferencias, porcentuales y anuales, los guarda en un DataFrame
        y luego indexa los valores fila por fila"""

        # Filtro de valores nulos iniciales/finales
        col = col[col.first_valid_index():col.last_valid_index()]

        freq = col.index.freq.freqstr
        series_id = col.name

        # Lista de intervalos temporales de pandas EN ORDEN
        periods = ['AS-JAN', 'QS-JAN', 'MS', 'W-SUN', 'D']
        for period in periods:
            if freq == period:
                break

            # Promedio
            avg_col = col.groupby(pd.TimeGrouper(period)).apply(lambda x: x.mean())
            avg_df = self.generate_interval_transformations_df(avg_col, period)
            avg_df.apply(self.elastic_index,
                         axis='columns',
                         args=(series_id, period, 'avg'))

            # Suma
            sum_col = col.groupby(pd.TimeGrouper(period)).apply(sum)
            sum_df = self.generate_interval_transformations_df(sum_col, period)
            sum_df.apply(self.elastic_index,
                         axis='columns',
                         args=(series_id, period, 'sum'))

            # End of period
            eop_col = col.groupby(pd.TimeGrouper(period)).apply(self.end_of_period)
            eop_df = self.generate_interval_transformations_df(eop_col, period)
            eop_df.apply(self.elastic_index,
                         axis='columns',
                         args=(series_id, period, 'end_of_period'))

        # Valor directo, "asignado" como promedio de un único valor
        transformations = self.generate_interval_transformations_df(col, freq)
        transformations.apply(self.elastic_index, axis='columns', args=(series_id, freq, 'avg'))

    @staticmethod
    def end_of_period(x):
        """Itera hasta encontrarse con el último valor no nulo del data frame"""
        value = np.nan
        i = -1
        while np.isnan(value):
            value = x.iloc[i]
            i -= 1
        return value

    @staticmethod
    def generate_interval_transformations_df(col, freq):
        df = pd.DataFrame()
        df[constants.VALUE] = col
        df[constants.CHANGE] = col.diff(1)
        df[constants.PCT_CHANGE] = col.pct_change(1, fill_method=None)
        df[constants.CHANGE_YEAR_AGO] = change_a_year_ago(col, freq)
        df[constants.PCT_CHANGE_YEAR_AGO] = pct_change_a_year_ago(col, freq)
        return df

    def elastic_index(self, row, series_id, interval, agg):
        """Arma el JSON entendible por el bulk request de ES y lo
        agrega a la lista de bulk_actions

        la fila tiene forma de iterable con los datos de un único
        valor de la serie: el valor real, su variación inmnediata,
        porcentual, etc
        """

        # Borrado de la parte de tiempo del timestamp
        timestamp = str(row.name)
        timestamp = timestamp[:timestamp.find('T')]
        interval = freq_pandas_to_interval(interval)
        action = {
            "_index": self.index,
            "_type": settings.TS_DOC_TYPE,
            "_id": None,
            "_source": {}
        }

        source = {
            settings.TS_TIME_INDEX_FIELD: timestamp,
            'series_id': series_id,
            "interval": interval,
            "aggregation": agg
        }

        for column, value in row.iteritems():
            if value is not None and np.isfinite(value):
                # Todo: buscar método más elegante para resolver precisión incorrecta de los valores
                # Ver issue: https://github.com/datosgobar/series-tiempo-ar-api/issues/63
                # Convertir el np.float64 a string logra evitar la pérdida de precision. Luego se
                # convierte a float de Python para preservar el tipado numérico del valor
                source[column] = float(str(value))

        action['_id'] = series_id + '-' + interval + '-' + agg + '-' + timestamp
        action['_source'] = source
        self.bulk_actions.append(action)
        self.indexed_fields.add(series_id)

    def _handle_missing_series(self, series_id):
        # Si no hay datos previos indexados, borro la entrada de la DB
        search = Search(using=self.elastic,
                        index=self.index).filter('match', series_id=series_id)
        results = search.execute()
        if not results:
            Field.objects.get(series_id=series_id).delete()
