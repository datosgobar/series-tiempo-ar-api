#! coding: utf-8

# Modos de representación de las series, calculados y guardados
# en el proceso de indexación
REP_MODES = [
    'value',
    'change',
    'change_a_year_ago',
    'percent_change',
    'percent_change_a_year_ago'
]

AGGREGATIONS = [
    'avg',
    'min',
    'max',
    'sum'
]

COLLAPSE_INTERVALS = [  # EN ORDEN DE MENOR A MAYOR
    'day',
    'month',
    'quarter',
    'semester',
    'year'
]

API_DEFAULT_VALUES = {
    'rep_mode': 'value',
    'collapse_aggregation': 'avg',
    'collapse': 'year',
    'start': 0,
    'limit': 100,
    'metadata': 'simple',
    'sort': 'asc',
    'format': 'json',
    'header': 'names'
}


METADATA_SETTINGS = [
    'simple',
    'full',
    'none',
    'only'
]

SORT_VALUES = [
    'asc',
    'desc'
]

CATALOG_SIMPLE_META_FIELDS = [
    'title',
    'dataset'
]

DATASET_SIMPLE_META_FIELDS = [
    'distribution',
    'title',
    'description',
    'issued',
    'source'
]

DISTRIBUTION_SIMPLE_META_FIELDS = [
    'field',
    'title',
    'downloadURL',
    'units',
]

FIELD_SIMPLE_META_FIELDS = [
    'id',
    'description',
    'units'
]

FORMAT_VALUES = [
    'json',
    'csv'
]

RESPONSE_ERROR_CODE = 400

VALID_CSV_HEADER_MODES = [
    'names',
    'ids'
]
