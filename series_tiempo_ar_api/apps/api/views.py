#! coding: utf-8
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
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


@csrf_exempt
def save_request(request):
    orig_request = request.POST.get('request')
    params = orig_request.get('querystring', "ERROR")
    ip_address = request.POST.get('client_ip', "ERROR")
    query = Query(ids="<ids>", args=params, ip_address=ip_address, params=json.dumps(request.POST))
    query.save()
    return HttpResponse("OK: " + json.dumps(request.POST))
