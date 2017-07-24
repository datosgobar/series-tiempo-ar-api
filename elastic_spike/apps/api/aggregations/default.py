#! coding: utf-8

from elasticsearch_dsl import Search

from elastic_spike.apps.api.aggregations.base_aggregation import BaseAggregation


class Default(BaseAggregation):
    name = 'valor directo'

    def execute(self, series, request_args, source_data=None):
        field = request_args.get('field', 'value')
        search = Search(index="indicators",
                        doc_type=series,
                        using=self.elastic).source(fields=[field])

        self.result = {
            'data': []
        }

        for hit in search.scan():
            element = {
                'timestamp': hit.meta.id,
                'value': hit[field]
            }
            self.result['data'].append(element)
            self.result['field'] = field
        return self.result
