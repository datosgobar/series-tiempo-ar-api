from django_datajsonar.models import Distribution
from elasticsearch_dsl import Search, Q, Index
from series_tiempo_ar_api.apps.management import meta_keys

KEY_DAYS_PAIRS = (
    (meta_keys.HITS_TOTAL, None),
    (meta_keys.HITS_30_DAYS, 30),
    (meta_keys.HITS_90_DAYS, 90),
    (meta_keys.HITS_180_DAYS, 180),
)


def update_popularity_metadata(distribution: Distribution):
    if not Index('query').exists():
        return

    series = distribution.field_set\
        .exclude(identifier='indice_tiempo')\
        .exclude(identifier=None)

    series_ids = series.values_list('identifier', flat=True)

    for meta_key, days in KEY_DAYS_PAIRS:
        hits = popularity_aggregation(series_ids, days)

        for serie in series:
            serie_hits = hits[serie.identifier].count.value
            serie.enhanced_meta.update_or_create(key=meta_key,
                                                 defaults={'value': serie_hits})


def popularity_aggregation(series_ids: str, days: int):
    s = Search(index='query')
    s.aggs \
        .bucket(name="hits_last_days",
                agg_type='filters',
                filters={serie_id: get_serie_filter(serie_id, days) for serie_id in series_ids})\
        .metric(name='count',
                agg_type='value_count',
                field='serie_id')
    s = s[:0]

    result = s.execute()
    return result.aggregations.hits_last_days.buckets


def get_serie_filter(serie_id: str, days: int) -> dict:
    filters = []
    if days is not None:
        filters.append(Q('range', timestamp={'gte': f'now-{days}d'}))

    filters.append(Q('term', serie_id=serie_id))
    return {'bool': {'filter': filters}}
