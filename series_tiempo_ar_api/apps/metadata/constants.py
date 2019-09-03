#! coding: utf-8

METADATA_ALIAS = 'metadata'
METADATA_DOC_TYPE = 'doc'

PARAM_LIMIT = 'limit'
PARAM_OFFSET = 'start'
PARAM_QUERYSTRING = 'q'
PARAM_AGGREGATIONS = 'aggregations'
PARAM_SORT_BY = 'sort_by'
PARAM_SORT = 'sort'

FILTER_ARGS = {
    # Pares nombre_arg: field del documento en elasticsearch
    'dataset_theme': 'dataset_theme',
    'units': 'units',
    'dataset_publisher_name': 'dataset_publisher_name',
    'dataset_source': 'dataset_source_keyword',
    'catalog_id': 'catalog_id',
}

SORT_BY_RELEVANCE = 'relevance'
SORT_BY_HITS_90_DAYS = 'hits_90_days'

SORT_ASCENDING = 'asc'
SORT_DESCENDING = 'desc'

PARAM_DEFAULT_VALUES = {
    PARAM_LIMIT: 10,
    PARAM_OFFSET: 0,
    PARAM_SORT_BY: SORT_BY_RELEVANCE,
    PARAM_SORT: SORT_DESCENDING
}

VALID_SORT_BY_VALUES = [SORT_BY_RELEVANCE, SORT_BY_HITS_90_DAYS]
VALID_SORT_VALUES = [SORT_ASCENDING, SORT_DESCENDING]

SORT_BY_MAPPING = {
    SORT_BY_HITS_90_DAYS: 'hits'
}

SORT_MAPPING = {
    SORT_ASCENDING: '',
    SORT_DESCENDING: '-'
}


ANALYZER = 'spanish_asciifold'
SYNONYM_FILTER = 'synonyms_filter'

DEFAULT_MIN_SCORE = 5
