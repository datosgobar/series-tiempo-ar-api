#! coding: utf-8
import os
import json

import unicodecsv
from django.conf import settings
from django_rq import job

from .models import Query
from .utils import kong_milliseconds_to_tzdatetime


@job("default")
def analytics(ids, args_string, ip_address, params, timestamp_milliseconds):
    params_json = json.dumps(params)
    timestamp = kong_milliseconds_to_tzdatetime(timestamp_milliseconds)
    query = Query(ids=ids, args=args_string, ip_address=ip_address, params=params_json, timestamp=timestamp)
    query.save()


@job("default")
def export():
    queryset = Query.objects.all()
    filepath = os.path.join(settings.PROTECTED_MEDIA_DIR, settings.ANALYTICS_CSV_FILENAME)

    fields = [
        Query.timestamp,
        Query.ip_address,
        Query.ids,
        Query.params
    ]

    with open(filepath, 'wb') as f:
        writer = unicodecsv.writer(f)
        # header
        writer.writerow([field.field_name for field in fields])
        for query in queryset.iterator():

            writer.writerow([getattr(query, field.field_name) for field in fields])
