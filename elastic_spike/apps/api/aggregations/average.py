#! coding: utf-8

from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch


class Average:
    def __init__(self):
        self.result = []

    def execute(self, doc_type, field, interval):
        self.result = []
        elastic = Elasticsearch()
        search = Search(index="indicators", doc_type=doc_type, using=elastic)
        # Le decimos a Elastic que no devuelva resultados, nos interesa solo
        # el aggregation
        search = search[:0]

        search.aggs.bucket('average',
                           'date_histogram',
                           field='timestamp',
                           interval=interval).metric('average',
                                                     'avg',
                                                     field=field)

        result = search.execute()
        for element in result.aggregations.average.buckets:
            timestamp = element['key_as_string']
            average = element['average']
            self.result.append({
                'date': timestamp,
                'value': average.value
            })

        return self.result
