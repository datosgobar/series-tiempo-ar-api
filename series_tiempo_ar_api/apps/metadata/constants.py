#! coding: utf-8

METADATA_ALIAS = 'metadata'
METADATA_DOC_TYPE = 'doc'

PARAM_LIMIT = 'limit'
PARAM_OFFSET = 'start'
PARAM_QUERYSTRING = 'q'
PARAM_AGGREGATIONS = 'aggregations'
PARAM_SORT_BY = 'sort_by'

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

PARAM_DEFAULT_VALUES = {
    PARAM_LIMIT: 10,
    PARAM_OFFSET: 0,
    PARAM_SORT_BY: SORT_BY_RELEVANCE
}

VALID_SORT_BY_VALUES = [SORT_BY_RELEVANCE, SORT_BY_HITS_90_DAYS]

SORT_BY_MAPPING = {
    SORT_BY_HITS_90_DAYS: 'hits'
}


ANALYZER = 'spanish_asciifold'
SYNONYM_FILTER = 'synonyms_filter'

DEFAULT_MIN_SCORE = 5
