from django.http import JsonResponse
from django.views.generic import View

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from elastic_spike.apps.api.aggregations.average import Average


class All(View):
    def get(self, request):
        elastic = Elasticsearch()
        search = Search(index="indicators").using(elastic)
        query = search.execute()
        return JsonResponse(query.to_dict(), safe=False)


class SearchAPI(View):
    def __init__(self, **kwargs):
        self.aggregations = {
            'average': Average()
        }
        super().__init__(**kwargs)

    def get(self, request):
        elastic = Elasticsearch()
        _type = request.GET.get('type', '')
        field = request.GET.get('field', 'value')
        collapse = request.GET.get('interval', 'year')
        search = Search(index="indicators",
                        doc_type=_type,
                        using=elastic).source([field, 'timestamp'])
        agg = request.GET.get('agg', None)
        if agg:
            return self.calculate_aggregation(agg, _type, field, collapse)

        result = {
            'hits': [],
            'count': 0
        }

        # Itera sobre los resultados de la query sin cargar todos en memoria
        for hit in search.scan():
            element = {
                'date': hit.timestamp,
                field: hit.__getattr__(field)
            }
            result['hits'].append(element)

        result['count'] = len(result['hits'])
        return JsonResponse(result, safe=False)

    def calculate_aggregation(self, aggr, _type, field, interval):
        aggregation = self.aggregations.get(aggr, None)
        if aggregation:
            result = aggregation.execute(_type, field, interval)
            return JsonResponse(result, safe=False)
        else:
            return JsonResponse({})
