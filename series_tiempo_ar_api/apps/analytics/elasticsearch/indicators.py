from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import transaction

from series_tiempo_ar_api.apps.analytics.elasticsearch.doc import SeriesQuery
from series_tiempo_ar_api.apps.analytics.models import HitsIndicator
from django_datajsonar.models import Field

from series_tiempo_ar_api.libs.datajsonar_repositories.series_repository import SeriesRepository


def calculate_hits_indicators(for_date: date):
    hits = get_day_hits(for_date)
    indicators = []
    for hit in hits:
        serie_id = hit.key
        hits = hit.doc_count
        indicators.append(HitsIndicator(serie_id=serie_id, date=for_date, hits=hits))

    with transaction.atomic():
        series_ids = map(lambda x: x.serie_id, indicators)
        HitsIndicator.objects.filter(date=for_date, serie_id__in=series_ids).delete()
        HitsIndicator.objects.bulk_create(indicators)


def get_day_hits(for_date):
    tomorrow = for_date + relativedelta(days=1)
    date_filter = {
        'gte': f'{for_date}',
        'lt': f'{tomorrow}'
    }

    search = SeriesQuery.search().filter('range', timestamp=date_filter)
    search.aggs.bucket(name='hits_last_days', agg_type='terms', field='serie_id', size=Field.objects.count())
    search = search[:0]

    result = search.execute()
    return result.aggregations.hits_last_days.buckets


def all_time_series():
    series_ids = SeriesRepository.get_available_series()\
        .values_list('identifier', flat=True)
    return series_ids
