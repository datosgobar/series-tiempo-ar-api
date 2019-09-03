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
SORT_BY_FREQUENCY = 'frequency'

PARAM_DEFAULT_VALUES = {
    PARAM_LIMIT: 10,
    PARAM_OFFSET: 0,
    PARAM_SORT_BY: SORT_BY_RELEVANCE
}

VALID_SORT_BY_VALUES = [SORT_BY_RELEVANCE, SORT_BY_HITS_90_DAYS]

SORT_BY_MAPPING = {
    SORT_BY_HITS_90_DAYS: 'hits',
    SORT_BY_FREQUENCY: 'periodicity_index'
}

PERIODICITY_KEYWORDS = [  # EN ORDEN DE MENOR A MAYOR FRECUENCIA
    'R/P1Y',
    'R/P6M',
    'R/P3M',
    'R/P1M',
    'R/P1W',
    'R/P1D'
]

ANALYZER = 'spanish_asciifold'
SYNONYM_FILTER = 'synonyms_filter'

DEFAULT_MIN_SCORE = 5
