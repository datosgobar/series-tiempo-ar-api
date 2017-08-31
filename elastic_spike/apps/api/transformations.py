#! coding: utf-8

import re
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from elasticsearch_dsl import Search, MultiSearch
from elasticsearch_dsl.query import Match


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


class Default(BaseAggregation):
    """Calcula el promedio de una serie en base a el parámetro 'interval'"""

    def execute(self):
        interval = self.args.get('interval', 'year')
        field = self.args.get('field', 'value')
        agg = self.args.get('agg', 'avg')

        search = Search(index="indicators",
                        doc_type=self.series,
                        using=self.elastic)

        # Le decimos a Elastic que no devuelva resultados, nos interesa solo
        # el aggregation
        search = search[:0]

        search.aggs.bucket('agg',
                           'date_histogram',
                           field='timestamp',
                           interval=interval).metric('agg',
                                                     agg,
                                                     field=field)

        search_result = search.execute()
        data = []
        for element in search_result.aggregations.agg.buckets:
            timestamp = element['key_as_string']
            average = element['agg']
            if average.value is None:
                self.errors.append("Valores no encontrados para el intervalo "
                                   "pedido. Pruebe con una granularidad mayor")
                break
            data.append({
                'timestamp': timestamp,
                'value': average.value
            })

        if not self.errors:
            self.data = data


class Value(BaseAggregation):

    def execute(self):
        search = self.generate_search()

        ms = MultiSearch(index="indicators", using=self.elastic)
        ms = ms.add(search)
        responses = ms.execute()

        data = []
        for response in responses:
            for hit in response:
                if hit.value is None:
                    self.errors.append("Valores no encontrados para el intervalo pedido. Pruebe con una granularidad mayor")
                    break
                data.append({
                    'timestamp': hit.timestamp,
                    'value': hit.value
                })

        if not self.errors:
            self.data = data

    def generate_search(self):
        """Crea el objeto search para pegarle a Elastic a partir de
        los parámetros pasados, de existir. Se especifica:
            * Intervalo de tiempo
            * Ordenamiento de resultados
            * Paginación de resultados
        """

        search = Search(index="indicators",
                        doc_type=self.series,
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
        start = self.args.get('start', 0)
        rows = self.args.get('rows', 100)
        search = search[start:rows]

        return search
