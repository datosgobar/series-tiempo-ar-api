#! coding: utf-8
import pandas as pd
from django.conf import settings

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from .base_query import BaseQuery
from series_tiempo_ar_api.apps.api.common.operations import change_a_year_ago, pct_change_a_year_ago
from series_tiempo_ar_api.apps.api.query import constants


class CollapseQuery(BaseQuery):
    """Calcula el promedio de una serie en base a una bucket
    aggregation
    """

    def __init__(self, index, other=None):
        super(CollapseQuery, self).__init__(index)
        # Datos guardados en la instancia para asegurar conmutabilidad
        # de operaciones
        self.collapse_interval = constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE]
        self.periodicity = self.collapse_interval

        if other:
            self.series = list(other.series)
            self.args = other.args.copy()
            # Inicializo con collapse default a las series
            self.add_collapse()

    def add_series(self, series_id, rep_mode, periodicity,
                   collapse_agg=constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]):
        self._init_series(series_id, rep_mode, collapse_agg)
        # Instancio agregación de collapse con parámetros default
        serie = self.series[-1]
        agg = serie.collapse_agg
        serie.search = self._add_aggregation(serie, agg)
        self.periodicity = self.collapse_interval

    def add_collapse(self, interval=None):
        if interval:
            # Temporalmente: convertir collapse semestral en anual,
            # Elasticsearch no los soporta
            if interval == 'semester':
                interval = 'year'

            self.collapse_interval = interval
            self.periodicity = self.collapse_interval

        for serie in self.series:
            agg = serie.collapse_agg
            serie.search = self._add_aggregation(serie, agg)

    def _add_aggregation(self, serie, collapse_agg):

        search = serie.search
        # Anula resultados de la búsqueda normal de ES, nos interesa solo resultados agregados
        search = search[:0]

        # Agrega el collapse de los datos según intervalo de tiempo
        bucket = search.aggs \
            .bucket(constants.COLLAPSE_AGG_NAME,
                    'date_histogram',
                    field=settings.TS_TIME_INDEX_FIELD,
                    interval=self.collapse_interval)

        if collapse_agg == constants.AGG_END_OF_PERIOD:
            rep_mode = serie.rep_mode
            bucket.metric(constants.COLLAPSE_AGG_NAME, 'scripted_metric',
                          init_script=constants.EOP_INIT,
                          map_script=constants.EOP_MAP % rep_mode,
                          reduce_script=constants.EOP_REDUCE)
        else:
            bucket.metric(constants.COLLAPSE_AGG_NAME,
                          collapse_agg,
                          field=constants.VALUE)

        return search

    def put_data(self, response, first_date_index, row_len, _=None):
        """Carga todos los datos de la respuesta en el objeto data, a partir
        del índice first_date_index de la misma, conformando una tabla con
        'row_len' datos por fila, llenando con nulls de ser necesario. Como en
        las queries de collapse no se puede filtrar previamente por offset de
        start y limit, se hace el filtrado manualmente
        """
        start = self.args['start']
        limit = self.args['limit']
        for i, hit in enumerate(response):
            if i < start:
                continue

            data = hit[constants.COLLAPSE_AGG_NAME].value
            data_offset = i - start  # Offset de la primera fecha donde va a ir el dato actual
            data_index = first_date_index + data_offset
            if data_offset >= limit:  # Ya conseguimos datos suficientes
                break
            if data_index == len(self.data):  # No hay row, inicializo
                timestamp = self._format_timestamp(hit['key_as_string'])
                self._init_row(timestamp, data, row_len)
            else:
                self.data[data_index].append(data)

    def _get_first_date(self, response):
        return self._format_timestamp(response[0]['key_as_string'])

    def _format_response(self, responses):
        for response in responses:
            # Smart solution
            hits = response.aggregations.agg.buckets
            self._format_single_response(hits)

        self._apply_transformations()

    def _apply_transformations(self):
        """Aplica las transformaciones del modo de representación de las series pedidas"""

        df, freq = self._init_df()

        for i, serie in enumerate(self.series, 1):
            if serie.rep_mode == constants.VALUE:
                pass
            elif serie.rep_mode == constants.CHANGE:
                df[i] = df[i].diff(1)
            elif serie.rep_mode == constants.PCT_CHANGE:
                df[i] = df[i].pct_change(1, fill_method=None)
            elif serie.rep_mode == constants.CHANGE_YEAR_AGO:
                df[i] = change_a_year_ago(df[i], freq)
            elif serie.rep_mode == constants.PCT_CHANGE_YEAR_AGO:
                df[i] = pct_change_a_year_ago(df[i], freq)

        df = df.where((pd.notnull(df)), None)  # Reemplaza valores nulos (NaN) por None de python
        self.data = df.reset_index().values.tolist()
        for row in self.data:
            row[0] = str(row[0].date())  # conversión de pandas Timestamp a date de Python

            # Fix a issue #63 de precisión de floats
            # https://github.com/datosgobar/series-tiempo-ar-api/issues/63
            for i, data in enumerate(row[1:], 1):
                row[i] = float(str(data)) if data is not None else data

        if self.args[constants.PARAM_SORT] == constants.SORT_DESCENDING:
            self.data.reverse()

    def _init_df(self):
        """Crea un pandas DataFrame de los datos obtenidos para facilitar el cálculo
        de transformaciones
        """
        df = pd.DataFrame(data=self.data)
        # Armado del índice de tiempo necesario para calcular transformaciones anuales
        translation = {
            'day': 'D',
            'week': 'W-MON',
            'month': 'MS',
            'quarter': 'QS',
            'year': 'AS'
        }
        freq = translation[self.collapse_interval]
        index = pd.date_range(self.data[0][0], self.data[-1][0],
                              freq=freq)
        df = df[df.columns[1:]]  # Index 0 == fecha, nuestras columnas de datos son de 1 en adelante
        df = df.set_index(index)
        return df, freq

    @staticmethod
    def _sort_responses(responses):
        def date_order_cmp(x, y):
            """Ordena por primera fecha de resultados del bucket aggregation"""

            hits_x = x.aggregations.agg.buckets
            hits_y = y.aggregations.agg.buckets

            if not hits_x or not hits_y:
                return 0

            first_date_x = hits_x[0]['key_as_string']
            first_date_y = hits_y[0]['key_as_string']
            if first_date_x == first_date_y:
                return 0

            if first_date_x < first_date_y:
                return -1
            return 1

        return sorted(responses, cmp=date_order_cmp)

    def has_collapse(self):
        return True

    def sort(self, how):
        if how not in constants.SORT_VALUES:
            raise QueryError

        self.args[constants.PARAM_SORT] = how
