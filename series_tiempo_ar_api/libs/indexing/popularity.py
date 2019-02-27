from django_datajsonar.models import Distribution
from elasticsearch_dsl import Q, Index, Search

from series_tiempo_ar_api.apps.analytics.elasticsearch.doc import SeriesQuery
from series_tiempo_ar_api.apps.management import meta_keys

KEY_DAYS_PAIRS = (
    (meta_keys.HITS_TOTAL, None),
    (meta_keys.HITS_30_DAYS, 30),
    (meta_keys.HITS_90_DAYS, 90),
    (meta_keys.HITS_180_DAYS, 180),
)


def update_popularity_metadata(distribution: Distribution):
    if not Index(SeriesQuery._doc_type.index).exists():
        return

    series = distribution.field_set\
        .exclude(title='indice_tiempo')\
        .exclude(identifier=None)

    series_ids = series.values_list('identifier', flat=True)

    if not series_ids:
        return

    for meta_key, days in KEY_DAYS_PAIRS:
        s = SeriesQuery.search()
        if days:
            s = s.filter('range', timestamp={'gte': f'now-{days}d/d'})
        buckets = {serie_id: get_serie_filter(serie_id) for serie_id in series_ids}
        agg_result = popularity_aggregation(s, buckets)

        update_series_popularity_metadata(agg_result, meta_key, series)


def update_series_popularity_metadata(agg_result, meta_key, series):
    for serie in series:
        serie_hits = get_hits(serie.identifier, agg_result)
        serie.enhanced_meta.update_or_create(key=meta_key,
                                             defaults={'value': serie_hits})


def get_hits(serie_id, agg_result):
    return agg_result[serie_id].count.value


def popularity_aggregation(search: Search, buckets):

    search.aggs \
        .bucket(name="hits_last_days",
                agg_type='filters',
                filters=buckets)\
        .metric(name='count',
                agg_type='value_count',
                field='serie_id')
    search = search[:0]

    result = search.execute()
    return result.aggregations.hits_last_days.buckets


def get_serie_filter(serie_id: str) -> dict:
    filters = [Q('term', serie_id=serie_id)]
    return {'bool': {'filter': filters}}
