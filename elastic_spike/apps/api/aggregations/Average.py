#! coding: utf-8

from elasticsearch_dsl import Search

from elastic_spike.apps.api.aggregations.BaseAggregation import BaseAggregation


class Average(BaseAggregation):
    def execute(self, request_args):
        doc_type = request_args.get('type')
        interval = request_args.get('interval', 'year')
        field = request_args.get('field', 'value')

        self.result.clear()
        search = Search(index="indicators",
                        doc_type=doc_type,
                        using=self.elastic)
        # Le decimos a Elastic que no devuelva resultados, nos interesa solo
        # el aggregation
        search = search[:0]

        search.aggs.bucket('average',
                           'date_histogram',
                           field='timestamp',
                           interval=interval).metric('average',
                                                     'avg',
                                                     field=field)

        search_result = search.execute()
        data = []
        for element in search_result.aggregations.average.buckets:
            timestamp = element['key_as_string']
            average = element['average']
            data.append({
                'date': timestamp,
                'value': average.value
            })

        self.result['data'] = data
        return self.result
