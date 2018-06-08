#! coding: utf-8
import os
import json

import iso8601
import requests
import unicodecsv
from dateutil.relativedelta import relativedelta
from django_rq import job
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import FieldError
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


def import_last_day_analytics_from_api_mgmt(limit=1000):
    today = timezone.now().date()
    yesterday = today - relativedelta(days=1)
    import_config_model = ImportConfig.get_solo()
    if (not import_config_model.endpoint or
            not import_config_model.token or
            not import_config_model.kong_api_id):
        raise FieldError("Configuración de importación de analytics no inicializada")

    response = import_config_model.get_results(from_date=yesterday, limit=limit)
    _load_queries_into_db(response)
    next_results = response['next']
    while next_results:
        response = requests.get(
            next_results,
            headers={'Authorization': 'Token {}'.format(import_config_model.token)}
        ).json()
        _load_queries_into_db(response)
        next_results = response['next']

    return response


def _load_queries_into_db(query_results):
    queries = []
    for result in query_results['results']:
        queries.append(Query(
            ip_address=result['ip_address'],
            args=result['querystring'],
            timestamp=iso8601.parse_date(result['start_time']),
            ids='nada',
            params='nada'
        ))

    Query.objects.bulk_create(queries)
