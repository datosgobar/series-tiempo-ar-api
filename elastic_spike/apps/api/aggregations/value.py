#! coding: utf-8
from elastic_spike.apps.api.aggregations.base_aggregation import BaseAggregation
from elasticsearch_dsl import Search


class Value(BaseAggregation):

    def execute(self, series, request_args):

        search = Search(index="indicators",
                        doc_type=series,
                        using=self.elastic)
        try:
            search = self.interval_filter(request_args.get('from'),
                                          request_args.get('to'),
                                          search)
        except ValueError:
            return self.result

        data = []
        for hit in search.scan():
            if hit.value is None:
                self.result['errors'].append("Valores no encontrados para el intervalo pedido. Pruebe con una granularidad mayor")
                break
            data.append({
                'timestamp': hit.timestamp,
                'value': hit.value
            })

        if not self.result['errors']:
            self.result['data'] = data

        self.calc_interval()
        return self.result

    def calc_interval(self):
        # first_date = self.result['data'][0]['timestamp']
        # second_date = self.result['data'][1]['timestamp']
        #
        # first_date = datetime.strptime(first_date, self.date_format)
        # second_date = datetime.strptime(second_date, self.date_format)
        #
        self.result['interval'] = "month"
