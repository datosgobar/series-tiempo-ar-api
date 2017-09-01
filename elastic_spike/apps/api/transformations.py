#! coding: utf-8

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
        ms = MultiSearch(index="indicators", using=self.elastic)
        for serie in self.series:
            search = self.generate_search(serie)
            ms = ms.add(search)

        responses = ms.execute()

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
        _to = self.args.get('to')
        _from = self.args.get('from')
        _filter = {
            'lte': _to,
            'gte': _from
        }
        search = search.filter('range', timestamp=_filter)

        search = search.sort('timestamp')

        # Paginación
        start = int(self.args.get('start', 0))
        limit = start + int(self.args.get('limit', 100))
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
