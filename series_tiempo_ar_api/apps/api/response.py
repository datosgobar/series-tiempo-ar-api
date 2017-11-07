#! coding: utf-8

"""Módulo con funciones generadoras de respuestas HTTP para llamadas
a la API
"""

from django.http.response import JsonResponse
from .query.query import Query


class ResponseGenerator(object):

    def __init__(self, _format):
        if _format == 'json':
            self.execute = JsonFormat().run

        elif _format == 'csv':
            pass

    def execute(self, query):
        raise NotImplementedError


class JsonFormat(object):
    def run(self, query, args):
        """Genera una respuesta JSON

        Args:
            query(Query): Query armada lista para ejecutar
            args (dict): argumentos de la llamada original
        """

        response = query.run()
        response['params'] = self._generate_params_field(query, args)
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
