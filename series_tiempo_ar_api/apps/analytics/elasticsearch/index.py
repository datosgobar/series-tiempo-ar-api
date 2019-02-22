import json
from json import JSONDecodeError

from elasticsearch.helpers import streaming_bulk, parallel_bulk
from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections
from iso8601 import iso8601

from series_tiempo_ar_api.apps.analytics.models import Query
from .doc import SeriesQuery
from series_tiempo_ar_api.apps.api.query import constants
from .constants import SERIES_QUERY_INDEX_NAME


class AnalyticsIndexer:

    def __init__(self, index: str = SERIES_QUERY_INDEX_NAME):
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
    for query in queryset.iterator():
        if not query.ids or query.status_code != 200:
            continue

        ids = query.ids.replace('\'', '"')
        series_ids_params = json.loads(ids)

        for ids_string in series_ids_params:
            for serie_string in ids_string.split(','):
                serie_string = serie_string.strip()
                if serie_string:
                    yield construct_query_doc(query, serie_string)


def _clean_date(date: str):
    try:
        return str(iso8601.parse_date(date).date())
    except iso8601.ParseError:
        return None


def _clean_params(params: dict) -> dict:
    clean_params = {}

    for param, values in params.items():
        if values[0]:
            clean_params[param] = values[0]

    for date_key in constants.DATE_KEYS:
        if date_key in clean_params:
            new_date = _clean_date(clean_params[date_key])
            if new_date:
                clean_params[date_key] = new_date
    return clean_params


def construct_query_doc(query: Query, serie_string) -> dict:
    params = read_params(query.params)

    serie_id = serie_string.split(':')[0]
    params.update(get_params(serie_string))
    params = _clean_params(params)
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


def read_params(params: str) -> dict:
    if not params:
        return {}

    try:
        return json.loads(params.replace('\'', '"'))
    except JSONDecodeError:  # Varios datos inválidos, no los indexo
        return {}


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
    if value in constants.REP_MODES:
        return constants.PARAM_REP_MODE
    elif value in constants.AGGREGATIONS:
        return constants.PARAM_COLLAPSE_AGG
