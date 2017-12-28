#! coding: utf-8
from django.http import HttpResponse
from ipware.ip import get_ip
from series_tiempo_ar_api.apps.api.query import constants
from .query.pipeline import QueryPipeline
from .query.analytics import analytics
from .models import Query


def query_view(request):
    query = QueryPipeline()
    # Formateo argumentos a lowercase, excepto ids
    ids = request.GET.get(constants.PARAM_IDS)
    args = {key: value.lower() for key, value in request.GET.items()}
    args[constants.PARAM_IDS] = ids

    response = query.run(args)
    if response.status_code == 200:
        ip_address = get_ip(request)
        args_string = request.GET.urlencode()
        analytics.delay(ids, args_string, ip_address, args)
    return response


def save_request(request):
    query = Query(ids="test", args="test", ip_address="127.0.0.1", params=request.POST)
    query.save()
    return HttpResponse("OK: " + request.POST)
