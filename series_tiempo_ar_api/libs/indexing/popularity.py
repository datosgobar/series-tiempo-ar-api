from django_datajsonar.models import Distribution
from elasticsearch_dsl import Search, Q, Index
from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.analytics.elasticsearch.index import SeriesQuery

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
    for serie in series:
        for meta_key, days in KEY_DAYS_PAIRS:
            hits = popularity_aggregation(serie.identifier, days)
            serie.enhanced_meta.update_or_create(key=meta_key,
                                                 defaults={'value': hits})


def popularity_aggregation(serie_id: str, days: int) -> int:
    filters = [Q('term', serie_id=serie_id)]
    if days is not None:
        filters.append(Q('range', timestamp={'gte': f'now-{days}d'}))

    s = Search(index='query')
    s.aggs \
        .bucket(name="hits_last_days",
                agg_type='filter',
                bool={'filter': filters}) \
        .metric(name='count',
                agg_type='value_count',
                field='serie_id')
    s = s[:0]

    result = s.execute()
    return result.aggregations.hits_last_days.count.value
