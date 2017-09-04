#! coding: utf-8

from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, MultiSearch


class BaseAggregation:
    date_format = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, series, request_args):
        self.data = []
        self.errors = []
        self.elastic = Elasticsearch()
        self.series = series
        self.args = request_args
        self.execute()

    def execute(self):
        raise NotImplementedError


class Value(BaseAggregation):

    def execute(self):
        multi_search = MultiSearch(index="indicators", using=self.elastic)
        for serie in self.series:
            search = self.generate_search(serie)
            multi_search = multi_search.add(search)

        responses = multi_search.execute()

        self.format_response(responses)

    def format_response(self, responses):
        for response in responses:
            self.populate_data(response, responses.index(response))

    def generate_search(self, serie):
        """Crea el objeto search de una serie para pegarle a Elastic
        a partir de los parámetros pasados, de existir. Se especifica:
            * Intervalo de tiempo
            * Ordenamiento de resultados
            * Paginación de resultados
        """

        search = Search(index="indicators",
                        doc_type=serie['name'],
                        using=self.elastic)

        # Si 'to' o 'from' son None, Elastic lo ignora
        start_date = self.args.get('start_date')
        end_date = self.args.get('end_date')
        _filter = {
            'lte': end_date,
            'gte': start_date
        }
        search = search.filter('range', timestamp=_filter)

        search = search.sort('timestamp')

        # Paginación
        default_start = settings.API_DEFAULT_VALUES['start']
        start = int(self.args.get('start', default_start))
        default_limit = settings.API_DEFAULT_VALUES['limit']
        limit = start + int(self.args.get('limit', default_limit))
        search = search[start:limit]

        return search

    def populate_data(self, response, response_index):
        rep_mode = self.series[response_index]['rep_mode']
        for i in range(len(response)):
            hit = response[i]
            if i == len(self.data):
                data_row = [hit.timestamp]
                self.data.append(data_row)

            self.data[i].append(hit[rep_mode])


class Collapse(BaseAggregation):
    """Calcula el promedio de una serie en base a el parámetro 'interval'"""
    def execute(self):
        multi_search = MultiSearch(index="indicators", using=self.elastic)
        for serie in self.series:
            search = self.generate_search(serie)
            multi_search = multi_search.add(search)

        responses = multi_search.execute()

        self.format_response(responses)

    def format_response(self, responses):
        for response in responses:
            self.populate_data(response)

    def generate_search(self, serie):
        """Crea el objeto search de una serie para pegarle a Elastic
        a partir de los parámetros pasados, de existir. Se especifica:
            * Intervalo de tiempo
            * Ordenamiento de resultados
            * Paginación de resultados
        """

        search = Search(index="indicators",
                        doc_type=serie['name'],
                        using=self.elastic)

        # Si 'to' o 'from' son None, Elastic lo ignora
        start_date = self.args.get('start_date')
        end_date = self.args.get('end_date')
        _filter = {
            'lte': end_date,
            'gte': start_date
        }
        search = search.filter('range', timestamp=_filter)

        search = search.sort('timestamp')

        # Le decimos a Elastic que no devuelva resultados, nos interesa solo
        # el aggregation
        search = search[:0]
        collapse = self.args.get('collapse')
        agg = self.args.get('collapse-aggregation', 'avg')

        search.aggs.bucket('agg',
                           'date_histogram',
                           field='timestamp',
                           interval=collapse).metric('agg',
                                                     agg,
                                                     field=serie['rep_mode'])

        return search

    def populate_data(self, response):
        default_limit = settings.API_DEFAULT_VALUES['limit']
        limit = int(self.args.get('limit', default_limit))
        for i in range(len(response.aggregations.agg.buckets)):
            if i >= limit:
                break
            hit = response.aggregations.agg.buckets[i]
            if i == len(self.data):
                data_row = [hit['key_as_string']]
                self.data.append(data_row)

            self.data[i].append(hit['agg'].value)
