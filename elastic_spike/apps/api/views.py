#! coding: utf-8

from django.http import JsonResponse
from django.views.generic import View

from elasticsearch import Elasticsearch
from elasticsearch.client.indices import IndicesClient
from elasticsearch_dsl import Search

from elastic_spike.apps.api.aggregations.Default import Default
from elastic_spike.apps.api.aggregations.Average import Average
from elastic_spike.apps.api.aggregations.Proportion import Proportion


class All(View):
    def get(self, request):
        elastic = Elasticsearch()
        search = Search(index="indicators").using(elastic)
        query = search.execute()
        return JsonResponse(query.to_dict(), safe=False)


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
                aggr = request.GET.get('agg', 'default')
                aggregation = self.aggregations.get(aggr)
                if not aggregation:
                    result['errors'].append(
                        {'error': 'Agregación inválida: {}'.format(aggr)}
                    )
                else:
                    result.update(aggregation.execute(series, request.GET))
                    result['count'] = len(result['data'])
                    result['aggregation'] = aggregation.name
        else:
            result['errors'].append(
                {'error': 'No se especificó una serie de tiempo'}
            )
        return JsonResponse(result)

    def init_aggregations(self):
        self.aggregations['average'] = Average()
        self.aggregations['default'] = Default()
        self.aggregations['proportion'] = Proportion()
