# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.shortcuts import render

from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance


def query(request):
    querystring = request.GET.get('q', None)

    if not querystring:
        return JsonResponse({'error': "Querystring vacío"})

    search_body = """
    {
      "query": {
        "fuzzy": {
          "_all": "pib"
        }
      }
    }"""
    return JsonResponse(ElasticInstance.get().search(index='metadata', body=search_body))