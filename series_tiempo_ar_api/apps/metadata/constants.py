#! coding: utf-8

FIELDS_INDEX = 'fields_meta'

PARAM_LIMIT = 'limit'
PARAM_OFFSET = 'start'
PARAM_QUERYSTRING = 'q'

FILTER_ARGS = {
    # Pares nombre_arg: field del documento en elasticsearch
    'dataset_theme': 'dataset_theme',
    'units': 'units',
    'dataset_publisher_name': 'dataset_publisher_name',
    'dataset_source': 'dataset_source_keyword',
    'catalog_id': 'catalog_id',
}


ANALYZER = 'spanish_asciifold'
SYNONYM_FILTER = 'synonyms_filter'