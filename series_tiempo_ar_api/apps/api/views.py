#! coding: utf-8

from series_tiempo_ar_api.apps.api.query.pipeline import QueryPipeline


def query_view(request):
    query = QueryPipeline()
    return query.run(request.GET.copy())
