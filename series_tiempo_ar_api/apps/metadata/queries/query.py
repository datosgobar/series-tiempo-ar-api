#! coding: utf-8
from elasticsearch_dsl import Search, Q, MultiSearch

from series_tiempo_ar_api.apps.metadata.models import MetadataConfig
from series_tiempo_ar_api.apps.metadata.queries.query_terms import setup_field_terms_search, format_response
from series_tiempo_ar_api.apps.metadata.utils import resolve_catalog_id_aliases
from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Metadata
from series_tiempo_ar_api.apps.metadata import strings, constants


class FieldSearchQuery:
    """Ejecuta una query de búsquerda de metadatos de Field, a través de Elasticsearch"""

    def __init__(self, args):
        self.args = args
        self.response = {}
        self.errors = []
        self.aggregations_keys = []

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

        multi_search = self.get_multi_search()

        responses = multi_search.execute()
        self.populate_response(responses[0])
        self.populate_aggregations(responses[1:])

        return self.response

    def populate_response(self, response):
        self.response = {
            'data': [],
            'count': response.hits.total
        }
        for hit in response:
            self.append_hit(hit)

        self.response[constants.PARAM_LIMIT] = self.args[constants.PARAM_LIMIT]
        self.response[constants.PARAM_OFFSET] = self.args[constants.PARAM_OFFSET]

    def append_hit(self, hit):
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
                'frequency': getattr(hit, 'periodicity', None),
                'time_index_start': start_date,
                'time_index_end': end_date,
                'units': getattr(hit, 'units', None),
                'hits_90_days': getattr(hit, 'hits', None),
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

    def get_multi_search(self):
        multi_search = MultiSearch()
        search = self.get_search()
        multi_search = multi_search.add(search)

        if self.args.get(constants.PARAM_AGGREGATIONS) is not None:
            multi_search = self.add_terms_aggregations(multi_search)

        return multi_search

    def get_search(self):
        search = Metadata.search(index=constants.METADATA_ALIAS)
        # search = search.sort('-hits')
        search = self.setup_query(search)
        offset = self.args[constants.PARAM_OFFSET]
        limit = self.args[constants.PARAM_LIMIT]
        search = search[offset:limit + offset]
        for arg, field in constants.FILTER_ARGS.items():
            search = self.add_filters(search, arg, field)

        search = search.extra(min_score=MetadataConfig.get_solo().min_score)
        return search

    def add_terms_aggregations(self, multi_search):
        for response_term, es_field_term in constants.FILTER_ARGS.items():
            self.aggregations_keys.append(response_term)
            agg_search = self.get_search()
            agg_search = setup_field_terms_search(es_field_term, agg_search)
            multi_search = multi_search.add(agg_search)
        return multi_search

    def append_error(self, msg):
        self.errors.append({'error': msg})

    def add_filters(self, search: Search, arg_name: str, field_name: str):
        """Agrega filtro por field_name al objeto search de Elasticsearch,
        obtenido desde el campo arg_name de la query.
        """

        terms = self.args.get(arg_name)
        if not terms:
            return search

        terms = terms.split('||')
        if arg_name == 'catalog_id':
            terms = resolve_catalog_id_aliases(terms)

        search = search.filter('terms', **{field_name: terms})

        return search

    def setup_query(self, search: Search):
        if self.args.get(constants.PARAM_QUERYSTRING) is None:
            return search

        queries = []
        for field, values in MetadataConfig.get_solo().query_config.items():
            queries.append(Q('bool', should=Q('match', **{field: self.args.get(constants.PARAM_QUERYSTRING)}), **values))
        return search.query('dis_max',
                            queries=queries)

    def populate_aggregations(self, aggregations_responses):
        if not aggregations_responses:
            return

        aggregations = {}
        for response, key in zip(aggregations_responses, self.aggregations_keys):
            aggregations[key] = [
                {'label': source['key'], 'series_count': source['doc_count']}
                for source in response.aggregations.results.buckets
            ]

        self.response['aggregations'] = aggregations
