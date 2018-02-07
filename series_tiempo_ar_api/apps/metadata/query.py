#! coding: utf-8
from elasticsearch_dsl import Search

from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance
from . import strings, constants


class FieldMetadataQuery(object):
    """Ejecuta una query de búsquerda de metadatos de Field, a través de Elasticsearch"""

    def __init__(self, args):
        self.args = args
        self.response = {}
        self.errors = []

    def validate(self):
        """Valida los parámetros de la query, actualizando la lista de errores de ser necesario"""
        limit = self.args.get(constants.PARAM_LIMIT, 10)
        try:
            self.args[constants.PARAM_LIMIT] = int(limit)
        except ValueError:
            self.append_error(strings.INVALID_PARAMETER.format(constants.PARAM_LIMIT, limit))

        offset = self.args.get(constants.PARAM_OFFSET, 0)
        try:
            self.args[constants.PARAM_OFFSET] = int(offset)
        except ValueError:
            self.append_error(strings.INVALID_PARAMETER.format(constants.PARAM_OFFSET, offset))

        if not self.args.get(constants.PARAM_QUERYSTRING):
            self.append_error(strings.EMPTY_QUERYSTRING)

    def execute(self):
        """Ejecuta la query. Devuelve un diccionario con el siguiente formato
        {
            "limit": 20,
            "offset": 0,
            "count": 1,
            "data": [
                {
                    "title": "foo",
                    "description": "bar",
                    "id": "if-foo",
               }
            ]
        }
        """

        self.validate()

        if self.errors:
            self.response['errors'] = self.errors
            return self.response

        es_client = ElasticInstance.get()

        querystring = self.args[constants.PARAM_QUERYSTRING]
        offset = self.args[constants.PARAM_OFFSET]
        limit = self.args[constants.PARAM_LIMIT]
        search = Search(using=es_client).query('match', _all=querystring)
        search = search[offset:limit]

        hits = search.execute()
        self.response = {
            'data': [],
            'count': 0
        }
        for hit in hits:
            self.response['data'].append({
                'id': hit.id,
                'description': hit.description,
                'title': hit.title,
            })

        self.response['count'] = len(self.response['data'])
        self.response['limit'] = self.args[constants.PARAM_LIMIT]
        self.response['offset'] = self.args[constants.PARAM_OFFSET]

        return self.response

    def append_error(self, msg):
        self.errors.append({'error': msg})
