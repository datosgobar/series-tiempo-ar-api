#! coding: utf-8
import os
import json

import iso8601
import unicodecsv
from dateutil.relativedelta import relativedelta
from django_rq import job
from django.conf import settings
from django.utils import timezone
from .models import Query, ImportConfig
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


def import_last_day_analytics():
    today = timezone.now().date()
    yesterday = today
    response = ImportConfig.get_solo().get_results(to_date=yesterday.strftime('%Y-%m-%d'))

    queries = []
    for result in response['results']:
        queries.append(Query(
            ip_address=result['ip_address'],
            args=result['querystring'],
            timestamp=iso8601.parse_date(result['start_time']),
            ids='nada',
            params='nada'
        ))

    Query.objects.bulk_create(queries)
    return response
