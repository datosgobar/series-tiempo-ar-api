from django.http import JsonResponse
from django.views.generic import View

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


class All(View):
    def get(self, request):
        elastic = Elasticsearch()
        search = Search(index="indicators").using(elastic)
        query = search.execute()
        return JsonResponse(query.to_dict(), safe=False)


class Oferta(View):
    def get(self, request):
        elastic = Elasticsearch()
        _type = request.GET.get('type', '')
        field = request.GET.get('field', 'value')

        search = Search(index="indicators",
                        doc_type=_type,
                        using=elastic).source([field, 'timestamp'])

        # agg = request.GET.get('agg', None)
        # if agg:
        #     s.aggs.bucket(agg, 'date_histogram',
        #                   field='timestamp',
        #                   interval='year').bucket('average', 'avg', field='value')

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
