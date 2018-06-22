#! coding: utf-8
import os
import json
import requests
import unicodecsv
from django_rq import job
from django.conf import settings
from django.utils import timezone

from .models import Query
from .utils import kong_milliseconds_to_tzdatetime
from .importer import AnalyticsImporter


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
        'timestamp': lambda x: timezone.localtime(x.timestamp),
        'ip_address': lambda x: x.ip_address,
        'ids': lambda x: x.ids,
        'params': lambda x: x.params,
    }

    with open(filepath, 'wb') as f:
        writer = unicodecsv.writer(f)
        # header
        writer.writerow([field for field in fields])
        for query in queryset.iterator():

            writer.writerow([val(query) for val in fields.values()])


@job('default', timeout=1000)
def import_last_day_analytics_from_api_mgmt(limit=1000, requests_lib=requests):
    AnalyticsImporter(limit, requests_lib).run()
