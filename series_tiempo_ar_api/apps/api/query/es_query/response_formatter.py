#! coding: utf-8
from iso8601 import iso8601

from series_tiempo_ar_api.apps.api.helpers import get_relative_delta
from series_tiempo_ar_api.apps.api.query import constants


class ResponseFormatter(object):

    def __init__(self, series, responses, args):
        self.series = series
        self.responses = responses
        self.data_dict = {}
        self.args = args

    def format_response(self):
        """Procesa la respuesta recibida de Elasticsearch, la guarda en
        el diccionario data_dict con el siguiente formato
        self.data_dict = {
          "1990-01-01": { "serie_1": valor1, "serie_2": valor2, ... },
          "1990-02-01": { "serie_1": valor1, "serie_2": valor2, ... }
        }
        Luego el diccionario es pasado a la lista de listas final
        self.data para conformar la respuesta esperada de lista de listas
        """
        final_data = []
        for i, response in enumerate(self.responses):
            rep_mode = self.series[i].rep_mode

            if self.series[i].collapse_agg in (constants.AGG_MIN, constants.AGG_MAX):
                for hit in response.aggregations.test.buckets:
                    data = hit['test']['value']
                    timestamp_dict = self.data_dict.setdefault(hit['key_as_string'], {})
                    timestamp_dict[self._data_dict_series_key(self.series[i])] = data
            else:
                response = filter(lambda hit: rep_mode in hit, response)
                for hit in response:
                    timestamp_dict = self.data_dict.setdefault(hit.timestamp, {})
                    series = self._data_dict_series_key(self.series[i])
                    timestamp_dict[series] = hit[rep_mode]

        if not self.data_dict:  # No hay datos
            return []

        self._make_date_index_continuous(min(self.data_dict.keys()),
                                         max(self.data_dict.keys()))

        for timestamp in sorted(self.data_dict.keys(),
                                reverse=self.args[constants.PARAM_SORT] != constants.SORT_ASCENDING):
            row = [timestamp]

            for series in self.series:
                row.append(self.data_dict[timestamp].get(self._data_dict_series_key(series)))

            final_data.append(row)

        return final_data

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
        if not self.data_dict:
            return

        current_date = iso8601.parse_date(start_date)
        end_date = iso8601.parse_date(end_date)

        while current_date < end_date:
            current_date += get_relative_delta(self.args[constants.PARAM_PERIODICITY])
            self.data_dict.setdefault(str(current_date.date()), {})
