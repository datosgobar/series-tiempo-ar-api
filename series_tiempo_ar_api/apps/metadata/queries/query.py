#! coding: utf-8
from elasticsearch_dsl import Search

from series_tiempo_ar_api.apps.metadata.utils import resolve_catalog_id_aliases
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
        search = Field.search(using=es_client)

        querystring = self.args.get(constants.PARAM_QUERYSTRING)
        if querystring is not None:
            search = search.query('match', all=querystring)

        offset = self.args[constants.PARAM_OFFSET]
        limit = self.args[constants.PARAM_LIMIT]
        search = search[offset:limit + offset]

        for arg, field in constants.FILTER_ARGS.items():
            search = self.add_filters(search, arg, field)

        response = search.execute()
        self.response = {
            'data': [],
            'count': response.hits.total
        }
        for hit in response:
            start_date = getattr(hit, 'start_date', None)
            if start_date:
                start_date = start_date.date()

            end_date = getattr(hit, 'end_date', None)
            if end_date:
                end_date = end_date.date()

            self.response['data'].append({
                'field': {
                    'id': getattr(hit, 'id', None),
                    'description': getattr(hit, 'description', None),
                    'title': getattr(hit, 'title', None),
                    'periodicity': getattr(hit, 'periodicity', None),
                    'start_date': start_date,
                    'end_date': end_date,
                    'units': getattr(hit, 'units', None),
                },
                'dataset': {
                    'title': getattr(hit, 'dataset_title', None),
                    'publisher': {
                        'name': getattr(hit, 'dataset_publisher_name', None),
                    },
                    'source': getattr(hit, 'dataset_source', None),
                    'theme': getattr(hit, 'dataset_theme', None),
                }
            })

        self.response[constants.PARAM_LIMIT] = self.args[constants.PARAM_LIMIT]
        self.response[constants.PARAM_OFFSET] = self.args[constants.PARAM_OFFSET]

        return self.response

    def append_error(self, msg):
        self.errors.append({'error': msg})

    def add_filters(self, search: Search, arg_name: str, field_name: str):
        """Agrega filtro por field_name al objeto search de Elasticsearch,
        obtenido desde el campo arg_name de la query.
        """

        terms = self.args.get(arg_name)
        if not terms:
            return search

        terms = terms.split(',')
        if arg_name == 'catalog_id':
            terms = resolve_catalog_id_aliases(terms)

        search = search.filter('terms', **{field_name: terms})

        return search
