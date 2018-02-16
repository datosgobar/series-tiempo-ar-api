# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .analytics import analytics


@csrf_exempt
def save(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    body = json.loads(request.body)
    req_data = body.get('request')
    if not req_data:  # Fatal error
        return HttpResponse(status=400)

    uri = req_data.get('uri')
    if 'admin/' in uri or 'api/' not in uri:
        return HttpResponse()

    params = req_data.get('querystring')
    ids = params.get('ids', 'No especificado')
    ip_address = body.get('client_ip')
    timestamp = body.get('started_at')
    args = req_data.get('request_uri', 'No especificado')

    params_start = args.find('?')
    if params_start > 0:
        args = args[params_start:]
    analytics.delay(ids, args, ip_address, params, timestamp)
    return HttpResponse()
