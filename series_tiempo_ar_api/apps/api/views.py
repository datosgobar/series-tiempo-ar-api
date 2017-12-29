#! coding: utf-8
from series_tiempo_ar_api.apps.api.query import constants
from .query.pipeline import QueryPipeline


def query_view(request):
    query = QueryPipeline()
    # Formateo argumentos a lowercase, excepto ids
    ids = request.GET.get(constants.PARAM_IDS)
    args = {key: value.lower() for key, value in request.GET.items()}
    args[constants.PARAM_IDS] = ids

    response = query.run(args)
    return response
