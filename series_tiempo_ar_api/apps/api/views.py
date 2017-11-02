#! coding: utf-8

from django.http import JsonResponse
from series_tiempo_ar_api.apps.api.pipeline import QueryPipeline


def query_view(request):
    query = QueryPipeline()
    return JsonResponse(query.run(request.GET.copy()))
