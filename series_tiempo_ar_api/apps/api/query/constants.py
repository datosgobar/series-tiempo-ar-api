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

PARAM_IDS = 'ids'
PARAM_REP_MODE = 'representation_mode'
PARAM_COLLAPSE_AGG = 'collapse_aggregation'
PARAM_COLLAPSE = 'collapse'
PARAM_START = 'start'
PARAM_LIMIT = 'limit'
PARAM_METADATA = 'metadata'
PARAM_SORT = 'sort'
PARAM_FORMAT = 'format'
PARAM_HEADER = 'header'
PARAM_START_DATE = 'start_date'
PARAM_END_DATE = 'end_date'


METADATA_SIMPLE = 'simple'
METADATA_FULL = 'full'
METADATA_ONLY = 'only'
METADATA_NONE = 'none'

METADATA_SETTINGS = [
    METADATA_SIMPLE,
    METADATA_FULL,
    METADATA_ONLY,
    METADATA_NONE
]

SORT_VALUES = [
    'asc',
    'desc'
]

API_DEFAULT_VALUES = {
    PARAM_REP_MODE: 'value',
    PARAM_COLLAPSE_AGG: 'avg',
    PARAM_COLLAPSE: 'year',
    PARAM_START: 0,
    PARAM_LIMIT: 100,
    PARAM_METADATA: METADATA_SIMPLE,
    PARAM_SORT: 'asc',
    PARAM_FORMAT: 'json',
    PARAM_HEADER: 'names'
}

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
