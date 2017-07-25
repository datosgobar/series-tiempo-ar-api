#! coding: utf-8

from django.http import JsonResponse
from django.views.generic import View

from elasticsearch import Elasticsearch
from elasticsearch.client.indices import IndicesClient
from elasticsearch_dsl import Search

from elastic_spike.apps.api.aggregations.average import Average
from elastic_spike.apps.api.aggregations.proportion import Proportion


class SearchAPI(View):
    def __init__(self, **kwargs):
        self.aggregations = {}
        self.init_aggregations()
        self.elastic = Elasticsearch()
        super().__init__(**kwargs)

    def get(self, request, series=None):
        result = {
            'data': [],
            'count': 0,
            'errors': []
        }

        if series:
            indices = IndicesClient(client=self.elastic)
            if not indices.exists_type(index="indicators", doc_type=series):
                result['errors'].append(
                    {'error': 'Serie inválida: {}'.format(series)}
                )
            else:
                aggr = request.GET.get('agg', 'avg')
                aggregation = self.aggregations.get(aggr)
                if not aggregation:
                    result['errors'].append(
                        {'error': 'Agregación inválida: {}'.format(aggr)}
                    )
                else:
                    # Ejecución de query
                    result.update(aggregation.execute(series,
                                                      request.GET.copy()))
                    result['count'] = len(result['data'])
                    aggr = request.GET.get('agg')
                    result['aggregation'] = aggr if aggr else 'valor directo'
                    result['series'] = [series]
        else:
            result['errors'].append(
                {'error': 'No se especificó una serie de tiempo'}
            )
        return JsonResponse(result)

    def init_aggregations(self):
        self.aggregations['avg'] = Average()
        self.aggregations['min'] = Average()
        self.aggregations['max'] = Average()
        self.aggregations['sum'] = Average()
        self.aggregations['proportion'] = Proportion()
