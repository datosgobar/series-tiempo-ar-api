# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse

from .query import FieldMetadataQuery


def search(request):
    query = FieldMetadataQuery(request.GET.copy())

    return JsonResponse(query.execute())
