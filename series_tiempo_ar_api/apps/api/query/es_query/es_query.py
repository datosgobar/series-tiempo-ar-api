#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import MultiSearch

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query import strings
from series_tiempo_ar_api.apps.api.query.es_query.response_formatter import ResponseFormatter
from series_tiempo_ar_api.apps.api.query.es_query.series import Serie


class ESQuery:
    """Representa una query de la API de series de tiempo, que termina
    devolviendo resultados de datos leídos de ElasticSearch"""

    def __init__(self, index):
        """
        args:
            index (str): Índice de Elasticsearch a ejecutar las queries.
        """
        self.index = index
        self.series = []
        self.data = None
        self.count = None
        self.start_dates = None
        self.reverse_results = False

        # Parámetros que deben ser guardados y accedidos varias veces
        self.args = {
            constants.PARAM_START: constants.API_DEFAULT_VALUES[constants.PARAM_START],
            constants.PARAM_LIMIT: constants.API_DEFAULT_VALUES[constants.PARAM_LIMIT],
            constants.PARAM_SORT: constants.API_DEFAULT_VALUES[constants.PARAM_SORT]
        }

    def add_series(self, series_id, rep_mode, periodicity,
                   collapse_agg=constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]):
        self._init_series(series_id, rep_mode, collapse_agg, periodicity)
        if constants.PARAM_PERIODICITY not in self.args:
            self.add_collapse(periodicity)

    def get_series_ids(self):
        """Devuelve una lista de series cargadas"""
        return [serie.series_id for serie in self.series]

    def sort(self, how):
        """Ordena los resultados por ascendiente o descendiente"""
        for serie in self.series:
            serie.sort(how)

        # Guardo el parámetro, necesario en el evento de hacer un collapse
        self.args[constants.PARAM_SORT] = how

    def add_collapse(self, interval):
        self.args[constants.PARAM_PERIODICITY] = interval
        for serie in self.series:
            serie.add_collapse(interval)

    def _init_series(self, series_id, rep_mode, collapse_agg, periodicity):
        self.series.append(Serie(series_id=series_id,
                                 index=self.index,
                                 rep_mode=rep_mode,
                                 periodicity=periodicity,
                                 collapse_agg=collapse_agg))

    def add_pagination(self, start, limit, start_dates=None):
        if not self.series:
            raise QueryError(strings.EMPTY_QUERY_ERROR)

        # Aplicamos paginación luego, por ahora guardamos los parámetros
        self.args[constants.PARAM_START] = start
        self.args[constants.PARAM_LIMIT] = limit
        self.start_dates = start_dates or {}

    def setup_series_pagination(self):
        for serie in self.series:
            serie.add_pagination(self.args[constants.PARAM_START],
                                 self.args[constants.PARAM_LIMIT],
                                 request_start_dates=self.start_dates)

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
                                   doc_type=settings.TS_DOC_TYPE)

        for serie in self.series:
            self.setup_series_pagination()
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
