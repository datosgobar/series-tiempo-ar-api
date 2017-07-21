#! coding: utf-8

from elasticsearch_dsl import Search

from elastic_spike.apps.api.aggregations.BaseAggregation import BaseAggregation


class Default(BaseAggregation):
    name = 'valor directo'

    def execute(self, series, request_args):
        field = request_args.get('field', 'value')
        search = Search(index="indicators",
                        doc_type=series,
                        using=self.elastic).source(fields=[field])

        self.result = {
            'data': []
        }



        for hit in search.scan():
            element = {
                'date': hit.meta.id,
                field: hit[field]
            }
            self.result['data'].append(element)
        return self.result
