#! coding: utf-8

from elasticsearch_dsl import Search
from elastic_spike.apps.api.aggregations.base_aggregation import BaseAggregation


class Default(BaseAggregation):
    """Calcula el promedio de una serie en base a el parámetro 'interval'"""

    def execute(self, series, request_args):
        interval = request_args.get('interval', 'year')
        field = request_args.get('field', 'value')
        agg = request_args.get('agg', 'avg')

        self.result['interval'] = interval

        search = Search(index="indicators",
                        doc_type=series,
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
                self.result['errors'].append("Valores no encontrados para el intervalo pedido. Pruebe con una granularidad mayor")
                break
            data.append({
                'timestamp': timestamp,
                'value': average.value
            })

        if not self.result['errors']:
            self.result['data'] = data
        return self.result
