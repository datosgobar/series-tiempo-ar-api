#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import Search, MultiSearch
from iso8601 import iso8601

from series_tiempo_ar_api.apps.api.helpers import get_relative_delta, find_index
from ..elastic import ElasticInstance
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query import strings
from series_tiempo_ar_api.apps.api.exceptions import QueryError
from .series import Series


class BaseQuery(object):
    def __init__(self, index):
        """
        Base común de ambas queries (común y con collapse)

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

    def run(self):
        """Ejecuta la query de todas las series agregadas. Devuelve una
        'tabla' (lista de listas) con los resultados, siendo cada columna
        una serie.
        """
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

    def add_series(self, series_id, rep_mode, periodicity):
        raise NotImplementedError

    def _init_series(self, series_id, rep_mode):
        search = Search(using=self.elastic, index=self.index)
        # Filtra los resultados por la serie pedida
        search = search.filter('match', series_id=series_id)
        self.series.append(Series(series_id=series_id,
                                  rep_mode=rep_mode,
                                  search=search))

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

    @staticmethod
    def _format_timestamp(timestamp):
        if timestamp.find('T') != -1:  # Borrado de la parte de tiempo
            return timestamp[:timestamp.find('T')]
        return timestamp

    def _format_single_response(self, response, **kwargs):
        """Formatea y agrega los datos de la respuesta de la búsqueda 'response'
        a la lista de datos self.data
        """
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

    def get_data_start_end_dates(self):
        if not self.data:
            return {}

        return {
            constants.PARAM_START_DATE: self.data[0][0],
            constants.PARAM_END_DATE: self.data[-1][0]
        }

    def put_data(self, response, first_date_index, new_row_len, param):
        raise NotImplementedError

    def _get_first_date(self, response):
        raise NotImplementedError

    def _format_response(self, responses):
        raise NotImplementedError

    def add_collapse(self, agg, interval):
        raise NotImplementedError
