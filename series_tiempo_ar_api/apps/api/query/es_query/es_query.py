#! coding: utf-8
from django.conf import settings

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query import strings
from .base_query import BaseQuery


class ESQuery(BaseQuery):
    """Representa una query de la API de series de tiempo, que termina
    devolviendo resultados de datos leídos de ElasticSearch"""

    def add_series(self, series_id, rep_mode, periodicity):
        self._init_series(series_id, rep_mode)
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
        raise QueryError(strings.INVALID_QUERY_TYPE)

    def has_collapse(self):
        return False
