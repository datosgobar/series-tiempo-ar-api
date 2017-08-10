#! coding: utf-8
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match

from .base_aggregation import BaseAggregation
from .default import Default


class Index(BaseAggregation):
    def execute(self, series, request_args):
        base = request_args.get('base')
        field = request_args.get('field', 'value')
        if not base:
            self.result['errors'].append("Base no especificada")
            return self.result

        request_args['agg'] = 'avg'
        search = Default().execute(series, request_args)
        search_data = search.get('data')
        if not search_data:
            self.result['errors'].extend(search.get('errors', []))
        else:
            search_base = Search(index="indicators",
                                 doc_type=series,
                                 using=self.elastic).filter()

            search_base.query = Match(timestamp=base)
            result = search_base.execute()
            if not len(result.hits.hits):
                self.result['errors'].append("Base errónea")
                return self.result

            self.result['base'] = result.hits.hits[0]['_id']
            base_value = result.hits.hits[0]['_source'][field]

            for data in search_data:
                data['value'] = data['value'] / base_value * 100
            self.result['data'] = search_data
        return self.result
