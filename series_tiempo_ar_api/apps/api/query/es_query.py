#! coding: utf-8
import iso8601
import pandas as pd
from django.conf import settings
from elasticsearch_dsl import Search, MultiSearch

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.helpers import find_index, get_relative_delta
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance
from series_tiempo_ar_api.apps.api.query import strings
from series_tiempo_ar_api.apps.api.query import constants
from ..common.operations import pct_change_a_year_ago, change_a_year_ago


class ESQuery(object):
    """Representa una query de la API de series de tiempo, que termina
    devolviendo resultados de datos leídos de ElasticSearch"""

    def __init__(self, index):
        """
        Instancia una nueva query

        args:
            index (str): Índice de Elasticsearch a ejecutar las queries.
        """
        self.index = index
        self.series = []
        self.elastic = ElasticInstance()
        self.data = []

        self.periodicity = None
        # Parámetros que deben ser guardados y accedidos varias veces
        self.args = {
            constants.PARAM_START: constants.API_DEFAULT_VALUES[constants.PARAM_START],
            constants.PARAM_LIMIT: constants.API_DEFAULT_VALUES[constants.PARAM_LIMIT],
            constants.PARAM_SORT: constants.API_DEFAULT_VALUES[constants.PARAM_SORT]
        }

    def add_pagination(self, start, limit):
        if not len(self.series):
            raise QueryError(strings.EMPTY_QUERY_ERROR)

        for serie in self.series:
            serie.search = serie.search[start:limit]

        # Guardo estos parámetros, necesarios en el evento de hacer un collapse
        self.args[constants.PARAM_START] = start
        self.args[constants.PARAM_LIMIT] = limit

    def add_filter(self, start=None, end=None):
        if not len(self.series):
            raise QueryError(strings.EMPTY_QUERY_ERROR)

        _filter = {
            'lte': end,
            'gte': start
        }
        for serie in self.series:
            # Agrega un filtro de rango temporal a la query de ES
            serie.search = serie.search.filter('range',
                                               timestamp=_filter)

    def add_series(self,
                   series_id,
                   rep_mode=constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE],
                   **kwargs):
        periodicity = kwargs['periodicity']
        self._init_series(series_id, rep_mode)
        self.periodicity = periodicity

    def run(self):
        if not self.series:
            raise QueryError(strings.EMPTY_QUERY_ERROR)

        multi_search = MultiSearch(index=self.index,
                                   doc_type=settings.TS_DOC_TYPE,
                                   using=self.elastic)

        for serie in self.series:
            search = serie.search
            multi_search = multi_search.add(search)

        responses = multi_search.execute()
        self._format_response(responses)
        return self.data

    def _format_response(self, responses):
        for i, response in enumerate(responses):
            rep_mode = self.series[i].rep_mode
            self._format_single_response(response, rep_mode=rep_mode)

    def _format_single_response(self, response, **kwargs):
        if not len(response):
            return

        first_date = self._get_first_date(response)

        # Agrego rows necesarios vacíos para garantizar continuidad
        self._make_date_index_continuous(date_up_to=first_date,
                                         time_delta=get_relative_delta(periodicity=self.periodicity))

        first_date_index = find_index(self.data, first_date)
        if first_date_index < 0:
            # indice no encontrado, vamos a appendear los resultados
            first_date_index = 0

        new_row_len = len(self.data[0]) + 1 if self.data else 2  # 1 timestamp + 1 dato = len 2
        self.put_data(response, first_date_index, new_row_len, **kwargs)

        # Consistencia del tamaño de las filas
        self._fill_data_with_nulls(row_len=new_row_len)

    def _get_first_date(self, response):
        return self._format_timestamp(response[0].timestamp)

    def put_data(self, response, start_index, row_len, **kwargs):
        rep_mode = kwargs['rep_mode']
        for i, hit in enumerate(response):
            data = hit[rep_mode] if rep_mode in hit else None
            data_offset = i  # Offset de la primera fecha donde va a ir el dato actual
            data_index = start_index + data_offset

            if data_index == len(self.data):  # No hay row, inicializo
                timestamp = self._format_timestamp(hit.timestamp)
                self._init_row(timestamp, data, row_len)
            else:
                self.data[data_index].append(data)

    def _init_series(self, series_id=None,
                     rep_mode=constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE]):

        search = Search(using=self.elastic, index=self.index)
        if series_id:
            # Filtra los resultados por la serie pedida
            search = search.filter('match', series_id=series_id)

        self.series.append(Series(series_id=series_id,
                                  rep_mode=rep_mode,
                                  search=search))

    @staticmethod
    def _format_timestamp(timestamp):
        if timestamp.find('T') != -1:  # Borrado de la parte de tiempo
            return timestamp[:timestamp.find('T')]
        return timestamp

    def get_series_ids(self):
        """Devuelve una lista de series cargadas"""
        return [serie.series_id for serie in self.series]

    def get_data_start_end_dates(self):
        if not self.data:
            return {}

        return {
            constants.PARAM_START_DATE: self.data[0][0],
            constants.PARAM_END_DATE: self.data[-1][0]
        }

    def sort(self, how):
        """Ordena los resultados por ascendiente o descendiente"""
        if how == constants.SORT_ASCENDING:
            order = settings.TS_TIME_INDEX_FIELD

        elif how == constants.SORT_DESCENDING:
            order = '-' + settings.TS_TIME_INDEX_FIELD
        else:
            msg = strings.INVALID_SORT_PARAMETER.format(how)
            raise ValueError(msg)

        for serie in self.series:
            serie.search = serie.search.sort(order)

        # Guardo el parámetro, necesario en el evento de hacer un collapse
        self.args[constants.PARAM_SORT] = how

    def _fill_data_with_nulls(self, row_len):
        """Rellena los espacios faltantes de la respuesta rellenando
        con nulls los datos faltantes hasta que toda fila tenga
        longitud 'row_len'
        """
        for row in self.data:
            while len(row) < row_len:
                row.append(None)

    def _make_date_index_continuous(self, date_up_to, time_delta):
        """Hace el índice de tiempo de los resultados continuo (según
        el intervalo de resultados), sin saltos, hasta la fecha
        especificada
        """

        # Si no hay datos cargados no hay nada que hacer
        if not len(self.data):
            return

        end_date = iso8601.parse_date(date_up_to)
        last_date = iso8601.parse_date(self.data[-1][0])
        delta = time_delta
        row_len = len(self.data[0])
        while last_date < end_date:
            last_date = last_date + delta
            date_str = self._format_timestamp(str(last_date.date()))
            row = [date_str]
            row.extend([None for _ in range(1, row_len)])
            self.data.append(row)

    def _init_row(self, timestamp, data, row_len):
        """Inicializa una nueva fila de los datos de respuesta,
        garantizando que tenga longitud row_len, que el primer valor
        sea el índice de tiempo, y el último el dato.
        """

        row = [timestamp]
        # Lleno de nulls el row menos 2 espacios (timestamp + el dato a agregar)
        nulls = [None] * (row_len - 2)
        row.extend(nulls)
        row.append(data)
        self.data.append(row)


class CollapseQuery(ESQuery):
    """Calcula el promedio de una serie en base a una bucket
    aggregation
    """

    def __init__(self, index, other=None):
        super(CollapseQuery, self).__init__(index)
        # Datos guardados en la instancia para asegurar conmutabilidad
        # de operaciones
        self.collapse_aggregation = \
            constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]
        self.collapse_interval = constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE]
        self.periodicity = self.collapse_interval

        if other:
            self.series = list(other.series)
            self.args = other.args.copy()
            # Inicializo con collapse default a las series
            self.add_collapse()

    def add_series(self,
                   series_id,
                   rep_mode=constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE],
                   **kwargs):
        kwargs['periodicity'] = None
        super(CollapseQuery, self).add_series(series_id, rep_mode, **kwargs)
        # Instancio agregación de collapse con parámetros default
        serie = self.series[-1]
        search = serie.search
        serie.search = self._add_aggregation(search)
        self.periodicity = self.collapse_interval

    def add_collapse(self, agg=None, interval=None):
        if agg:
            self.collapse_aggregation = agg
        if interval:
            # Temporalmente: convertir collapse semestral en anual,
            # Elasticsearch no los soporta
            if interval == 'semester':
                interval = 'year'

            self.collapse_interval = interval
            self.periodicity = self.collapse_interval

        for serie in self.series:
            search = serie.search
            serie.search = self._add_aggregation(search)

    def _add_aggregation(self, search):
        search = search[:0]
        # Agrega el collapse de los datos según intervalo de tiempo
        search.aggs \
            .bucket(constants.COLLAPSE_AGG_NAME,
                    'date_histogram',
                    field=settings.TS_TIME_INDEX_FIELD,
                    interval=self.collapse_interval) \
            .metric(constants.COLLAPSE_AGG_NAME,
                    self.collapse_aggregation,
                    field='value')

        return search

    def put_data(self, response, first_date_index, row_len, **kwargs):
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
        responses_sorted = self._sort_responses(responses)

        for response in responses_sorted:
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
                row[i] = round(data, 12) if data is not None else data

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


class Series(object):
    def __init__(self, series_id=None, rep_mode=None, search=None):
        self.series_id = series_id
        self.rep_mode = rep_mode
        self.search = search or Search()
        self.meta = None

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def get(self, item, default=None):
        return getattr(self, item, default)
