#! coding: utf-8
import os
import json

import unicodecsv
from django.conf import settings
from django_rq import job
from django.utils.timezone import localtime
from .models import Query
from .utils import kong_milliseconds_to_tzdatetime


@job("default")
def analytics(ids, args_string, ip_address, params, timestamp_milliseconds):
    params_json = json.dumps(params)
    timestamp = kong_milliseconds_to_tzdatetime(timestamp_milliseconds)
    query = Query(ids=ids, args=args_string, ip_address=ip_address, params=params_json, timestamp=timestamp)
    query.save()


@job("default")
def export(path=None):
    queryset = Query.objects.all()
    filepath = path or os.path.join(settings.PROTECTED_MEDIA_DIR, settings.ANALYTICS_CSV_FILENAME)

    fields = {
        'timestamp': lambda x: localtime(x.timestamp),
        'ip_address': lambda x: x.ip_address,
        'ids': lambda x: x.ids,
        'params': lambda x: x.params,
    }

    with open(filepath, 'wb') as f:
        writer = unicodecsv.writer(f)
        # header
        writer.writerow([field for field in fields.keys()])
        for query in queryset.iterator():

            writer.writerow([val(query) for val in fields.values()])
