#! coding: utf-8
import json

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from series_tiempo_ar import TimeSeriesDataJson
from series_tiempo_ar.validations import get_distribution_errors


@require_POST
@csrf_exempt
def validator_view(request):
    request_body = json.loads(request.body.decode('utf8'))
    catalog_url = request_body.get('catalog_url')
    distribution_id = request_body.get('distribution_id')
    if not (catalog_url and distribution_id):
        msg = "catalog_url y distribution_id son parametros obligatorios"
        return HttpResponseBadRequest(msg)
    report = {'catalog_url': catalog_url,
              'distribution_id': distribution_id, }
    try:
        datajson = TimeSeriesDataJson(catalog_url)
        error_list = get_distribution_errors(datajson, distribution_id)
        found_issues = len(error_list)
        detail = [err.args[0] for err in error_list]
    except Exception as e:
        found_issues = 1
        detail = str(e)
    report['found_issues'] = found_issues
    report['detail'] = detail
    return JsonResponse(report, json_dumps_params={'indent': 4})
