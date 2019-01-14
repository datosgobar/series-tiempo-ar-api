#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import MultiSearch

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query import strings
from series_tiempo_ar_api.apps.api.query.es_query.response_formatter import ResponseFormatter
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
        self.data = None
        self.count = None
        self.reverse_results = False

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

        self.args[constants.PARAM_PERIODICITY] = periodicity
        self._init_series(series_id, rep_mode, collapse_agg)

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
        self.args[constants.PARAM_PERIODICITY] = interval

    def _init_series(self, series_id, rep_mode, collapse_agg):
        self.series.append(Series(series_id=series_id,
                                  index=self.index,
                                  rep_mode=rep_mode,
                                  args=self.args,
                                  collapse_agg=collapse_agg))

    def add_pagination(self, start, limit, start_dates=None):
        if start_dates is None:
            start_dates = {}

        if not self.series:
            raise QueryError(strings.EMPTY_QUERY_ERROR)

        for serie in self.series:
            serie.add_pagination(start, limit, request_start_dates=start_dates)

        # Guardo estos parámetros, necesarios en el evento de hacer un collapse
        self.args[constants.PARAM_START] = start
        self.args[constants.PARAM_LIMIT] = limit

    def add_filter(self, start=None, end=None):
        if not self.series:
            raise QueryError(strings.EMPTY_QUERY_ERROR)

        for serie in self.series:
            serie.add_range_filter(start, end)

    def get_data_start_end_dates(self):
        if not self.data:
            return {}

        return {
            constants.PARAM_START_DATE: self.data[0][0],
            constants.PARAM_END_DATE: self.data[-1][0]
        }

    def execute_searches(self):
        """Ejecuta la query de todas las series agregadas, e inicializa
        los atributos data y count a partir de las respuestas.
        """
        if not self.series:
            raise QueryError(strings.EMPTY_QUERY_ERROR)

        multi_search = MultiSearch(index=self.index,
                                   doc_type=settings.TS_DOC_TYPE,
                                   using=self.elastic)

        for serie in self.series:
            serie.add_collapse(self.args[constants.PARAM_PERIODICITY])
            multi_search = multi_search.add(serie.search)

        responses = multi_search.execute()
        formatter = ResponseFormatter(self.series, responses, self.args)
        self.data = formatter.format_response()

        self.count = max([response.hits.total for response in responses])

    def get_results_data(self) -> list:
        if self.data is None:
            raise RuntimeError(strings.DATA_NOT_INITIALIZED)

        # Devuelvo hasta LIMIT values
        data = self.data[:self.args[constants.PARAM_LIMIT]]

        if self.reverse_results:
            data.reverse()
        return data

    def get_results_count(self) -> int:
        if self.count is None:
            raise RuntimeError(strings.DATA_NOT_INITIALIZED)

        return self.count

    def run(self) -> list:
        """Equivalente a execute_searches + get_results_data"""
        self.execute_searches()
        return self.get_results_data()

    def reverse(self):
        self.reverse_results = True
