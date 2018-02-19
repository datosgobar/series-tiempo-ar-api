# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json

import sendfile
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .tasks import analytics, export


@csrf_exempt
def save(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    body = json.loads(request.body)
    req_data = body.get('request')
    if not req_data:  # Fatal error
        return HttpResponse(status=400)

    if 'api/' not in req_data.get('uri'):
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


def read_analytics(request):
    if not request.user.is_staff:
        raise Http404

    return sendfile.sendfile(request, os.path.join(settings.PROTECTED_MEDIA_DIR, 'analytics.csv'))


def export_analytics(request):
    if not request.user.is_staff:
        raise Http404

    export.delay()
    return HttpResponse(render(request, 'export.html'))
