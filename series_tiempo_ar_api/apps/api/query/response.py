#! coding: utf-8

"""Módulo con funciones generadoras de respuestas HTTP para llamadas
a la API
"""
import unicodecsv
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse

from series_tiempo_ar_api.apps.api.exceptions import InvalidFormatError
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.series_ids_parser import SeriesIdsParser


class BaseFormatter:
    def run(self, query, query_args):
        raise NotImplementedError


class JsonFormatter(BaseFormatter):
    def run(self, query, query_args):
        """Genera una respuesta JSON"""

        response = query.run()
        response['params'] = self._generate_params_field(query, query_args)
        return JsonResponse(response)

    @staticmethod
    def _generate_params_field(query, args):
        """Genera el campo adicional de parámetros pasados de la
        respuesta. Contiene todos los argumentos pasados en la llamada,
        más una lista de identifiers de field, distribution y dataset
        por cada serie pedida
        """
        params = args.copy()
        params['identifiers'] = query.get_series_identifiers()
        return params


class CSVFormatter(BaseFormatter):
    def run(self, query, query_args):
        """Genera una respuesta CSV, con columnas
        (indice tiempo, serie1, serie2, ...) y un dato por fila
        """

        # Saco metadatos, no se usan para el formato CSV
        query.set_metadata_config(constants.METADATA_NONE)

        header = query_args.get(constants.PARAM_HEADER,
                                constants.API_DEFAULT_VALUES[constants.PARAM_HEADER])

        ids_parser = SeriesIdsParser(query.series_rep_modes, query.get_series_ids(how=header))
        series_ids = ids_parser.parse(header)
        data = query.run()['data']

        response = HttpResponse(content_type='text/csv')
        content = 'attachment; filename="{}"'
        response['Content-Disposition'] = content.format(constants.CSV_RESPONSE_FILENAME)

        delim = query_args.get(constants.PARAM_DELIM,
                               constants.API_DEFAULT_VALUES[constants.PARAM_DELIM])
        writer = unicodecsv.writer(response, delimiter=str(delim))
        header = [settings.INDEX_COLUMN] + series_ids

        writer.writerow(header)
        decimal_char = query_args.get(constants.PARAM_DEC_CHAR, '.')
        if decimal_char != '.':
            # Reemplazo los puntos decimales por el char pedido
            for row in data:
                row = [str(el).replace('.', decimal_char) if el else None for el in row]
                writer.writerow(row)
        else:
            for row in data:
                writer.writerow(row)

        return response


class ResponseFormatterGenerator:

    formatters = {
        constants.FORMAT_JSON: JsonFormatter,
        constants.FORMAT_CSV: CSVFormatter
    }

    def __init__(self, _format):
        if self.formatters.get(_format) is None:
            raise InvalidFormatError

        self.formatter = self.formatters[_format]

    def get_formatter(self):
        return self.formatter()
