#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import MultiSearch, Q, Search
from iso8601 import iso8601

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.helpers import get_relative_delta, find_index
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query import strings
from series_tiempo_ar_api.apps.api.query.es_query.series import Series
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class ESQuery(object):
    """Representa una query de la API de series de tiempo, que termina
    devolviendo resultados de datos leídos de ElasticSearch"""

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

        self.has_end_of_period = False

    def add_series(self, series_id, rep_mode, periodicity,
                   collapse_agg=constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]):
        # Fix a casos en donde collapse agg no es avg pero los valores serían iguales a avg
        # Estos valores no son indexados! Entonces seteamos la aggregation a avg manualmente
        if periodicity == constants.COLLAPSE_INTERVALS[-1]:
            collapse_agg = constants.AGG_DEFAULT

        self._init_series(series_id, rep_mode, collapse_agg)
        self.periodicity = periodicity

    def _format_response(self, responses):
        for i, response in enumerate(responses):
            rep_mode = self.series[i].rep_mode
            self._format_single_response(response, rep_mode=rep_mode)

    def _get_first_date(self, response):
        return self._format_timestamp(response[0].timestamp)

    def put_data(self, response, start_index, row_len, **kwargs):
        """Carga todos los datos de la respuesta en el objeto data, a partir
        del índice first_date_index de la misma, conformando una tabla con
        'row_len' datos por fila, llenando con nulls de ser necesario
        """
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

    def get_series_ids(self):
        """Devuelve una lista de series cargadas"""
        return [serie.series_id for serie in self.series]

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

    def add_collapse(self, interval):
        self.periodicity = interval

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
            search = search.filter('bool',
                                   must=[Q('match', interval=self.periodicity)])
            multi_search = multi_search.add(search)
            if serie.collapse_agg == constants.AGG_END_OF_PERIOD:
                self.has_end_of_period = True

        responses = multi_search.execute()
        self._format_response(responses)
        # Devuelvo hasta LIMIT values
        return self.data[:self.args[constants.PARAM_LIMIT]]

    def _init_series(self, series_id, rep_mode, collapse_agg):
        search = Search(using=self.elastic, index=self.index)
        # Filtra los resultados por la serie pedida
        search = search.filter('bool',
                               must=[Q('match', series_id=series_id),
                                     Q('match', aggregation=collapse_agg)])
        self.series.append(Series(series_id=series_id,
                                  rep_mode=rep_mode,
                                  search=search,
                                  collapse_agg=collapse_agg))

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

    def _make_date_index_continuous(self, target_date, time_delta):
        """Hace el índice de tiempo de los resultados continuo (según
        el intervalo de resultados), sin saltos, hasta la fecha
        especificada
        """

        # Si no hay datos cargados no hay nada que hacer
        if not len(self.data):
            return

        # Caso fecha target > última fecha (rellenar al final)
        target_date = iso8601.parse_date(target_date)
        last_date = iso8601.parse_date(self.data[-1][0])
        delta = time_delta
        row_len = len(self.data[0])
        while last_date < target_date:
            last_date = last_date + delta
            date_str = self._format_timestamp(str(last_date.date()))
            row = [date_str]
            row.extend([None for _ in range(1, row_len)])
            self.data.append(row)

        # Caso fecha target < primera fecha (rellenar al principio)
        first_date = iso8601.parse_date(self.data[0][0])
        lead_rows = []
        current_date = target_date
        while current_date < first_date:
            date_str = self._format_timestamp(str(current_date.date()))
            row = [date_str]
            row.extend([None for _ in range(1, row_len)])
            lead_rows.append(row)
            current_date = current_date + delta

        lead_rows.extend(self.data)
        self.data = lead_rows

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
        self._make_date_index_continuous(target_date=first_date,
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
