# -*- coding: utf-8 -*-
# pylint: disable=W0613
from __future__ import unicode_literals

from django.http import JsonResponse

from series_tiempo_ar_api.apps.metadata.queries.query_terms import query_field_terms
from series_tiempo_ar_api.apps.metadata.queries.query import FieldSearchQuery


def search(request):
    query = FieldSearchQuery(request.GET.copy())

    return JsonResponse(query.execute())


def dataset_source(request):
    response = query_field_terms(field='dataset_source_keyword')

    return JsonResponse(response)


def field_units(request):
    response = query_field_terms(field='units')

    return JsonResponse(response)


def dataset_publisher_name(request):
    response = query_field_terms(field='dataset_publisher_name')

    return JsonResponse(response)


def dataset_theme(request):
    response = query_field_terms(field='dataset_theme')

    return JsonResponse(response)


def catalog_id(request):
    response = query_field_terms(field='catalog_id')

    return JsonResponse(response)
