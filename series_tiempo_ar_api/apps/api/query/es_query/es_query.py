#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import MultiSearch, Q, Search
from iso8601 import iso8601

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.helpers import get_relative_delta
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query import strings
from series_tiempo_ar_api.apps.api.query.es_query.series import Series
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class ESQuery(object):
    """Representa una query de la API de series de tiempo, que termina
    devolviendo resultados de datos leídos de ElasticSearch"""

    def __init__(self, index):
        """
        args:
            index (str): Índice de Elasticsearch a ejecutar las queries.
        """
        self.index = index
        self.series = []
        self.elastic = ElasticInstance()
        self.data = []

        self.data_dict = {}
        self.periodicity = None
        # Parámetros que deben ser guardados y accedidos varias veces
        self.args = {
            constants.PARAM_START: constants.API_DEFAULT_VALUES[constants.PARAM_START],
            constants.PARAM_LIMIT: constants.API_DEFAULT_VALUES[constants.PARAM_LIMIT],
            constants.PARAM_SORT: constants.API_DEFAULT_VALUES[constants.PARAM_SORT]
        }

    def add_series(self, series_id, rep_mode, periodicity,
                   collapse_agg=constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]):
        # Fix a casos en donde collapse agg no es avg pero los valores serían iguales a avg
        # Estos valores no son indexados! Entonces seteamos la aggregation a avg manualmente
        if periodicity == constants.COLLAPSE_INTERVALS[-1]:
            collapse_agg = constants.AGG_DEFAULT

        self._init_series(series_id, rep_mode, collapse_agg)
        self.periodicity = periodicity

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

    def _init_series(self, series_id, rep_mode, collapse_agg):
        search = Search(using=self.elastic, index=self.index)
        end = self.args[constants.PARAM_START] + self.args[constants.PARAM_LIMIT]
        search = search[self.args[constants.PARAM_START]:end]
        search = search.sort(settings.TS_TIME_INDEX_FIELD)  # Default: ascending sort
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

    def get_data_start_end_dates(self):
        if not self.data:
            return {}

        return {
            constants.PARAM_START_DATE: self.data[0][0],
            constants.PARAM_END_DATE: self.data[-1][0]
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
            search = search.filter('bool',
                                   must=[Q('match', interval=self.periodicity)])
            multi_search = multi_search.add(search)

        responses = multi_search.execute()
        self._format_response(responses)
        # Devuelvo hasta LIMIT values
        return self.data[:self.args[constants.PARAM_LIMIT]]

    def _format_response(self, responses):
        """Procesa la respuesta recibida de Elasticsearch, la guarda en
        el diccionario data_dict con el siguiente formato
        self.data_dict = {
          "1990-01-01": { "serie_1": valor1, "serie_2": valor2, ... },
          "1990-02-01": { "serie_1": valor1, "serie_2": valor2, ... }
        }
        Luego el diccionario es pasado a la lista de listas final
        self.data para conformar la respuesta esperada de lista de listas
        """

        for i, response in enumerate(responses):
            rep_mode = self.series[i].rep_mode

            for hit in response:
                data = hit[rep_mode] if rep_mode in hit else None
                timestamp_dict = self.data_dict.setdefault(hit.timestamp, {})
                timestamp_dict[self._data_dict_series_key(self.series[i])] = data

        if not self.data_dict:  # No hay datos
            return

        self._make_date_index_continuous(min(self.data_dict.keys()),
                                         max(self.data_dict.keys()))

        # Ordeno las timestamp según si el sort es asc o desc usando función de comparación
        def cmp_func(one, other):
            if one == other:
                return 0

            if self.args[constants.PARAM_SORT] == constants.SORT_ASCENDING:
                return -1 if one < other else 1
            else:
                return 1 if one < other else -1

        for timestamp in sorted(self.data_dict.keys(), cmp=cmp_func):
            row = [timestamp]

            for series in self.series:
                row.append(self.data_dict[timestamp].get(self._data_dict_series_key(series)))

            self.data.append(row)

    @staticmethod
    def _data_dict_series_key(series):
        """Key única para identificar la serie pedida en el data_dict armado. Evita
        que se pisen series en queries que piden la misma serie con distintos rep modes
        o aggs (ver issue #243)
        """
        return series.series_id + series.rep_mode + series.collapse_agg

    def _make_date_index_continuous(self, start_date, end_date):
        """Hace el índice de tiempo de los resultados continuo (según
        el intervalo de resultados), sin saltos, entre start_date y end_date.
        Esto implica llenar el diccionario self.data_dict con claves de los
        timestamp faltantes para asegurar la continuidad
        """

        # Si no hay datos cargados no hay nada que hacer
        if not len(self.data_dict):
            return

        current_date = iso8601.parse_date(start_date)
        end_date = iso8601.parse_date(end_date)

        while current_date < end_date:
            current_date += get_relative_delta(self.periodicity)
            self.data_dict.setdefault(unicode(current_date.date()), {})
