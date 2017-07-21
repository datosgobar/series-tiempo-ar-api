#! coding: utf-8

from elasticsearch_dsl import Search

from elastic_spike.apps.api.aggregations.BaseAggregation import BaseAggregation


class Default(BaseAggregation):
    def execute(self, request_args):
        doc_type = request_args.get('type')
        field = request_args.get('field', 'value')
        search = Search(index="indicators",
                        doc_type=doc_type,
                        using=self.elastic).source(fields=[field])

        self.result = {
            'data': []
        }
        for hit in search.scan():
            element = {
                'date': hit.meta.id,
                field: hit.__getattr__(field)
            }
            self.result['data'].append(element)
        return self.result
