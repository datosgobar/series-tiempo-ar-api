#! coding: utf-8

"""Módulo con funciones generadoras de respuestas HTTP para llamadas
a la API
"""
import unicodecsv
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse

from series_tiempo_ar_api.apps.api.exceptions import InvalidFormatError


class BaseFormatter(object):
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
        query.set_metadata_config('none')

        series_ids = query.get_series_ids()
        data = query.run()['data']

        response = HttpResponse(content_type='text/csv')
        content = 'attachment; filename="{}.csv"'
        filename = series_ids[0]
        for serie in series_ids[1:]:
            filename += ',' + serie

        response['Content-Disposition'] = content.format(filename)

        writer = unicodecsv.writer(response)
        header = [settings.INDEX_COLUMN] + series_ids
        writer.writerow(header)
        for row in data:
            writer.writerow(row)

        return response


class ResponseFormatterGenerator(object):

    formatters = {
        'json': JsonFormatter,
        'csv': CSVFormatter
    }

    def __init__(self, _format):
        if self.formatters.get(_format) is None:
            raise InvalidFormatError

        self.formatter = self.formatters[_format]

    def get_formatter(self):
        return self.formatter()
