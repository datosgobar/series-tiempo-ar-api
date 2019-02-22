from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import transaction
from elasticsearch_dsl import Q

from series_tiempo_ar_api.apps.analytics.models import HitsIndicator
from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.indexing.popularity import popularity_aggregation


def calculate_hits_indicators(for_date: date):
    series_ids = all_time_series()
    chunk_size = 50
    for i in range(chunk_size):
        chunk = series_ids[chunk_size*i:chunk_size*(i+1)]
        calculate_hits_indicators_for_series(for_date, chunk)


def calculate_hits_indicators_for_series(for_date, series_ids):
    hits = get_day_hits(series_ids, for_date)
    indicators = []
    for key in hits:
        serie_hits = hits[key].count.value
        indicators.append(HitsIndicator(serie_id=key, date=for_date, hits=serie_hits))
    with transaction.atomic():
        HitsIndicator.objects.filter(date=for_date, serie_id__in=series_ids).delete()
        HitsIndicator.objects.bulk_create(indicators)


def get_day_hits(series_ids, for_date):
    buckets = {serie_id: get_serie_filter(serie_id, for_date) for serie_id in series_ids}
    return popularity_aggregation(buckets)


def all_time_series():
    series_ids = Field.objects \
        .filter(enhanced_meta__key=meta_keys.AVAILABLE)\
        .exclude(title='indice_tiempo') \
        .exclude(identifier=None) \
        .values_list('identifier', flat=True)
    return series_ids


def get_serie_filter(serie_id: str, for_date: date) -> dict:
    tomorrow = for_date + relativedelta(days=1)
    date_filter = {
        'gte': f'{for_date}',
        'lt': f'{tomorrow}'
    }
    filters = []

    if for_date is not None:
        filters.append(Q('range', timestamp=date_filter))

    filters.append(Q('term', serie_id=serie_id))
    return {'bool': {'filter': filters}}
