#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import MultiSearch

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
        self.count = None
        self.reverse_results = False

        # Parámetros que deben ser guardados y accedidos varias veces
        self.args = {
            constants.PARAM_LIMIT: constants.API_DEFAULT_VALUES[constants.PARAM_LIMIT],
            constants.PARAM_START: constants.API_DEFAULT_VALUES[constants.PARAM_START],
            constants.PARAM_SORT: constants.API_DEFAULT_VALUES[constants.PARAM_SORT]
        }

    def add_series(self, series_id, rep_mode, periodicity,
                   collapse_agg=constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]):
        self._init_series(series_id, rep_mode, collapse_agg, periodicity)
        if constants.PARAM_PERIODICITY not in self.args:
            self.add_collapse(periodicity)

    def sort(self, how):
        """Ordena los resultados por ascendiente o descendiente"""
        self.args[constants.PARAM_SORT] = how

    def add_collapse(self, interval):
        self.args[constants.PARAM_PERIODICITY] = interval

    def _init_series(self, series_id, rep_mode, collapse_agg, periodicity):
        self.series.append(Serie(series_id=series_id,
                                 index=self.index,
                                 rep_mode=rep_mode,
                                 periodicity=periodicity,
                                 collapse_agg=collapse_agg))

    def add_pagination(self, start, limit):
        self.args[constants.PARAM_START] = start
        self.args[constants.PARAM_LIMIT] = limit

    def add_filter(self, start=None, end=None):
        self.args[constants.PARAM_START_DATE] = start
        self.args[constants.PARAM_END_DATE] = end

    def get_results_count(self) -> int:
        if self.count is None:
            raise RuntimeError(strings.DATA_NOT_INITIALIZED)

        return self.count

    def reverse(self):
        self.reverse_results = True

    def run_for_series(self, series):
        self.series = []
        for serie in series:
            self.series.append(Serie(index=self.index,
                                     series_id=serie.identifier(),
                                     rep_mode=serie.rep_mode,
                                     periodicity=serie.periodicity(),
                                     collapse_agg=serie.collapse_agg()))

        start_dates = {serie.get_identifiers()['id']: serie.start_date() for serie in series}

        for serie in self.series:
            serie.add_pagination(self.args[constants.PARAM_START],
                                 self.args[constants.PARAM_LIMIT],
                                 start_dates or {})

        if self.args.get(constants.PARAM_PERIODICITY):
            for serie in self.series:
                serie.add_collapse(self.args.get(constants.PARAM_PERIODICITY))
        else:
            self.args[constants.PARAM_PERIODICITY] = self.series[0].periodicity

        if self.args.get(constants.PARAM_START_DATE) or self.args.get(constants.PARAM_END_DATE):
            for serie in self.series:
                serie.add_range_filter(self.args.get(constants.PARAM_START_DATE),
                                       self.args.get(constants.PARAM_END_DATE))

        for serie in self.series:
            serie.sort(self.args[constants.PARAM_SORT])

        return self._run()

    def _run(self) -> dict:
        """Equivalente a execute_searches + get_results_data"""
        result = self.execute_searches()

        # Devuelvo hasta LIMIT values
        result['data'] = result['data'][:self.args[constants.PARAM_LIMIT]]

        if self.reverse_results:
            result['data'].reverse()
        return result

    def execute_searches(self):
        """Ejecuta la query de todas las series agregadas, e inicializa
        los atributos data y count a partir de las respuestas.
        """

        multi_search = MultiSearch(index=self.index,
                                   doc_type=settings.TS_DOC_TYPE)

        for serie in self.series:
            multi_search = multi_search.add(serie.search)

        responses = multi_search.execute()
        formatter = ResponseFormatter(self.series, responses, self.args)

        return {
            'data': (formatter.format_response()),
            'count': max([response.hits.total for response in responses])
        }
