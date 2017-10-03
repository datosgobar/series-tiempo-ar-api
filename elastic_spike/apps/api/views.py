#! coding: utf-8

from django.http import JsonResponse
from elastic_spike.apps.api.pipeline import QueryPipeline


def query_view(request):
    query = QueryPipeline(request.GET.copy())
    return JsonResponse(query.result)
