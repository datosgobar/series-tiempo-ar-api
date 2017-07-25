#! coding: utf-8

from elasticsearch_dsl import Search

from elastic_spike.apps.api.aggregations.base_aggregation import BaseAggregation


class Average(BaseAggregation):
    """Calcula el promedio de una serie en base a el parámetro 'interval'"""
    name = "promedio"

    def execute(self, series, request_args, source_data=None):
        interval = request_args.get('interval', 'year')
        field = request_args.get('field', 'value')
        agg = request_args.get('agg')
        self.result.clear()
        search = Search(index="indicators",
                        doc_type=series,
                        using=self.elastic)

        _from = request_args.get('from')
        _to = request_args.get('to')

        _filter = {
            'lte': _to,
            'gte': _from
        }
        search = search.filter('range', timestamp=_filter)

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
            data.append({
                'timestamp': timestamp,
                'value': average.value
            })

        self.result['data'] = data
        self.result['interval'] = interval
        return self.result
