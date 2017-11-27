#! coding: utf-8
from ..elastic import ElasticInstance
from .. import constants
from .. import strings
from series_tiempo_ar_api.apps.api.exceptions import QueryError


class BaseQuery(object):
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
