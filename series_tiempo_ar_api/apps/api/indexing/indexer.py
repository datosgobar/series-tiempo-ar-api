#! coding: utf-8
import logging

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from django.conf import settings
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl import Search
from series_tiempo_ar.helpers import freq_iso_to_pandas

from series_tiempo_ar_api.apps.api.helpers import freq_pandas_to_index_offset
from series_tiempo_ar_api.apps.api.models import Distribution, Field
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance

from series_tiempo_ar_api.apps.api.indexing import strings
from series_tiempo_ar_api.apps.api.indexing import constants

# Ignora divisiones por cero, no nos molesta el NaN
np.seterr(divide='ignore', invalid='ignore')

logger = logging.Logger(__name__)
logger.addHandler(logging.StreamHandler())


class Indexer(object):
    """Lee distribuciones y las indexa a través de un bulk create en
    Elasticsearch
    """

    default_value = 0

    def __init__(self, index=settings.TS_INDEX):
        self.elastic = ElasticInstance()
        self.index = index
        self.indexed_fields = set()
        self.bulk_actions = []

    def run(self, distributions=None):
        """Indexa en Elasticsearch todos los datos de las
        distribuciones guardadas en la base de datos, o las
        especificadas por el iterable 'distributions'
        """
        self.init_index()

        # Optimización: Desactivo el refresh de los datos mientras indexo
        self.elastic.indices.put_settings(
            index=self.index,
            body=constants.DEACTIVATE_REFRESH_BODY
        )

        logger.info(strings.INDEX_START)

        for distribution in distributions:
            fields = distribution.field_set.all()
            fields = {field.title: field.series_id for field in fields}
            df = self.init_df(distribution, fields)

            self.generate_properties(df, fields)

        logger.info(strings.BULK_REQUEST_START)

        for success, info in parallel_bulk(self.elastic, self.bulk_actions):
            if not success:
                logger.warn(strings.BULK_REQUEST_ERROR, info)

        logger.info(strings.BULK_REQUEST_END)

        # Reactivo el proceso de replicado una vez finalizado
        self.elastic.indices.put_settings(
            index=self.index,
            body=constants.REACTIVATE_REFRESH_BODY
        )
        segments = constants.FORCE_MERGE_SEGMENTS
        self.elastic.indices.forcemerge(index=self.index,
                                        max_num_segments=segments)

        logger.info(strings.INDEX_END)

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
        columns = df.columns

        data = np.array(df)
        freq = freq_iso_to_pandas(distribution.periodicity)
        new_index = pd.date_range(df.index[0], df.index[-1], freq=freq)

        # Chequeo de series de días hábiles (business days)
        if freq == constants.DAILY_FREQ and new_index.size > df.index.size:
            new_index = pd.date_range(df.index[0],
                                      df.index[-1],
                                      freq=constants.BUSINESS_DAILY_FREQ)

        return pd.DataFrame(index=new_index, data=data, columns=columns)

    def init_index(self):
        if not self.elastic.indices.exists(self.index):
            self.elastic.indices.create(self.index,
                                        body=constants.INDEX_CREATION_BODY)

    def generate_properties(self, df, fields):
        df.apply(self.process_column, args=[fields])

        # Manejo de series faltantes
        for series_id in fields.values():
            if series_id not in self.indexed_fields:
                logger.info(strings.SERIES_NOT_FOUND, series_id)
                self._handle_missing_series(series_id)

    def process_column(self, col, fields):
        """Procesa una columna del DataFrame: calcula los valores de
        diferencias, porcentuales y anuales, los guarda en un DataFrame
        y luego indexa los valores fila por fila"""

        # Filtro de valores nulos iniciales/finales
        col = col[col.first_valid_index():col.last_valid_index()]

        freq = col.index.freq.freqstr
        df = pd.DataFrame()
        df[constants.VALUE] = col
        df[constants.CHANGE] = col.diff(1)
        df[constants.PCT_CHANGE] = col.pct_change(1, fill_method=None)
        df[constants.CHANGE_YEAR_AGO] = \
            self._year_ago_column(col, self._change, freq)
        df[constants.PCT_CHANGE_YEAR_AGO] = \
            self._year_ago_column(col, self._pct_change, freq)

        df.apply(self.elastic_index, axis='columns', args=(fields[col.name],))

    def elastic_index(self, row, series_id):
        """Arma el JSON entendible por el bulk request de ES y lo
        agrega a la lista de bulk_actions

        la fila tiene forma de iterable con los datos de un único
        valor de la serie: el valor real, su variación inmnediata,
        porcentual, etc
        """

        # Borrado de la parte de tiempo del timestamp
        timestamp = str(row.name)
        timestamp = timestamp[:timestamp.find('T')]

        action = {
            "_index": self.index,
            "_type": settings.TS_DOC_TYPE,
            "_id": None,
            "_source": {}
        }

        source = {
            settings.TS_TIME_INDEX_FIELD: timestamp,
            'series_id': series_id
        }

        for column, value in row.iteritems():
            if value is not None and np.isfinite(value):
                source[column] = value

        action['_id'] = series_id + '-' + timestamp
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

    def _get_value(self, df, col, index):
        """Devuelve el valor del df[col][index] o nan si no es válido.
        Evita Cargar Infinity y NaN en Elasticsearch
        """
        if index not in df[col]:
            return self.default_value

        return df[col][index] if np.isfinite(df[col][index]) else \
            self.default_value

    def _year_ago_column(self, col, operation, freq):
        """Aplica operación entre los datos de una columna y su valor
        un año antes. Devuelve una nueva serie de pandas
        """
        array = []
        offset = freq_pandas_to_index_offset(freq) or 0
        if offset:
            values = col.values
            array = operation(values[offset:], values[:-offset])
        else:
            for idx, val in col.iteritems():
                value = self._get_value_a_year_ago(idx, col, validate=True)
                if value != self.default_value:
                    array.append(operation(val, value))
                else:
                    array.append(None)

        return pd.Series(array, index=col.index[offset:])

    def _get_value_a_year_ago(self, idx, col, validate=False):
        """Devuelve el valor de la serie determinada por df[col] un
        año antes del índice de tiempo 'idx'. Hace validación de si
        existe el índice o no según 'validate' (operación costosa)
        """

        value = self.default_value
        year_ago_idx = idx.date() - relativedelta(years=1)
        if not validate:
            if year_ago_idx not in col.index:
                return self.default_value

            value = col[year_ago_idx]
        else:
            if year_ago_idx in col:
                value = col[year_ago_idx]

        return value

    def _pct_change(self, x, y):
        if isinstance(y, int) and y == 0:
            return self.default_value
        return x - y / y

    @staticmethod
    def _change(x, y):
        return x - y
