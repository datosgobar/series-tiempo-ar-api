#! coding: utf-8
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field

from series_tiempo_ar_api.apps.metadata import strings, constants


class FieldSearchQuery(object):
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
        search = Field.search(using=es_client).query('match', _all=querystring)
        search = search[offset:limit + offset]

        for arg, field in constants.FILTER_ARGS.items():
            search = self.add_filters(search, arg, field)

        response = search.execute()
        self.response = {
            'data': [],
            'count': response.hits.total
        }
        for hit in response:
            self.response['data'].append({
                'id': hit['id'],
                'description': hit['description'],
                'title': hit['title'],
            })

        self.response['limit'] = self.args[constants.PARAM_LIMIT]
        self.response['offset'] = self.args[constants.PARAM_OFFSET]

        return self.response

    def append_error(self, msg):
        self.errors.append({'error': msg})

    def add_filters(self, search, arg_name, field_name):
        """Agrega filtro por field_name al objeto search de Elasticsearch,
        obtenido desde el campo arg_name de la query.
        """
        units = self.args.get(arg_name)
        if units:
            units = units.split(',')
            search = search.filter('terms', **{field_name: units})

        return search
