#! coding: utf-8
import json

import unicodecsv
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
    with open('protected/analytics.csv', 'wb') as f:
        writer = unicodecsv.writer(f)

        # header
        writer.writerow(['timestamp', 'ip_address', 'ids', 'params'])
        for query in queryset.iterator():

            writer.writerow([query.timestamp, query.ip_address, query.ids, query.params])
