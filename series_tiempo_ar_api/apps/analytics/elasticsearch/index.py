import json

from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections

from . import constants
from .doc import SeriesQuery
from .constants import \
    REP_MODES, AGGREGATIONS, PARAM_REP_MODE, PARAM_COLLAPSE_AGG


class AnalyticsIndexer:

    def __init__(self, index: str = constants.SERIES_QUERY_INDEX_NAME):
        self.es_index = Index(index)
        self.es_index.doc_type(SeriesQuery)
        self.es_connection = connections.get_connection()

    def index(self, queryset):
        self._init_index()

        for success, info in parallel_bulk(self.es_connection, generate_es_query(queryset)):
            if not success:
                raise RuntimeError(f"Error indexando query a ES: {info}")

    def _init_index(self):
        if not self.es_index.exists():
            self.es_index.create()


def generate_es_query(queryset):
    for query in queryset:
        series_ids = json.loads(query.ids)

        for serie_string in series_ids:
            yield construct_query_doc(query, serie_string)


def construct_query_doc(query, serie_string) -> dict:
    params = json.loads(query.params) if query.params else {}

    serie_id = serie_string.split(':')[0]
    params.update(get_params(serie_string))
    return SeriesQuery(
        meta={'id': f'{query.id}-{serie_id}'},
        serie_id=serie_id,
        params=params,
        ip_address=query.ip_address,
        user_agent=query.user_agent,
        timestamp=query.timestamp,
        request_time=query.request_time,
        status_code=query.status_code
    ).to_dict(include_meta=True)


def get_params(serie_id: str) -> dict:
    terms = serie_id.split(':')

    result = {
        'ids': serie_id
    }

    for term in terms[1:]:
        key = _infer_param_key(term)
        if key is not None:
            result[key] = term

    return result


def _infer_param_key(value):
    if value in REP_MODES:
        return PARAM_REP_MODE
    elif value in AGGREGATIONS:
        return PARAM_COLLAPSE_AGG
