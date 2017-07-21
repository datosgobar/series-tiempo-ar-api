#! coding: utf-8

from django.http import JsonResponse
from django.views.generic import View

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from elastic_spike.apps.api.aggregations.Default import Default
from elastic_spike.apps.api.aggregations.Average import Average


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
        super().__init__(**kwargs)

    def get(self, request):
        result = {
            'data': [],
            'count': 0
        }

        aggr = request.GET.get('agg', 'default')
        aggregation = self.aggregations.get(aggr)
        result.update(aggregation.execute(request.GET))
        result['count'] = len(result['data'])
        return JsonResponse(result)

    def init_aggregations(self):
        self.aggregations['average'] = Average()
        self.aggregations['default'] = Default()
