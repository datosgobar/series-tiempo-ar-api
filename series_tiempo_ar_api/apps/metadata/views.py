# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse

from series_tiempo_ar_api.apps.metadata.queries.dataset_source import dataset_source_query
from series_tiempo_ar_api.apps.metadata.queries.query import FieldSearchQuery


def search(request):
    query = FieldSearchQuery(request.GET.copy())

    return JsonResponse(query.execute())


def dataset_source(request):
    response = dataset_source_query()

    return JsonResponse(response)
