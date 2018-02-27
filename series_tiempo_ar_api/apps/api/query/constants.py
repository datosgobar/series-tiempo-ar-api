#! coding: utf-8

from series_tiempo_ar_api.libs.indexing.constants import \
    VALUE, CHANGE, PCT_CHANGE, CHANGE_YEAR_AGO, PCT_CHANGE_YEAR_AGO

# Modos de representación de las series, calculados y guardados
# en el proceso de indexación
REP_MODES = [
    VALUE,
    CHANGE,
    PCT_CHANGE,
    CHANGE_YEAR_AGO,
    PCT_CHANGE_YEAR_AGO
]

AGG_DEFAULT = 'avg'
AGG_SUM = 'sum'
AGG_END_OF_PERIOD = 'end_of_period'
AGGREGATIONS = [
    AGG_DEFAULT,
    AGG_SUM,
    AGG_END_OF_PERIOD,
]

COLLAPSE_INTERVALS = [  # EN ORDEN DE MENOR A MAYOR
    'day',
    'week',
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
PARAM_DELIM = 'sep'
PARAM_DEC_CHAR = 'decimal'

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

SORT_ASCENDING = 'asc'
SORT_DESCENDING = 'desc'
SORT_VALUES = [
    SORT_ASCENDING,
    SORT_DESCENDING
]

HEADER_PARAM_NAMES = 'titles'
HEADER_PARAM_IDS = 'ids'
HEADER_PARAM_DESCRIPTIONS = 'descriptions'
VALID_CSV_HEADER_VALUES = [
    HEADER_PARAM_NAMES,
    HEADER_PARAM_IDS,
    HEADER_PARAM_DESCRIPTIONS,
]

FORMAT_JSON = 'json'
FORMAT_CSV = 'csv'
FORMAT_VALUES = [
    FORMAT_JSON,
    FORMAT_CSV
]

API_DEFAULT_VALUES = {
    PARAM_REP_MODE: 'value',
    PARAM_COLLAPSE_AGG: 'avg',
    PARAM_COLLAPSE: 'year',
    PARAM_START: 0,
    PARAM_LIMIT: 100,
    PARAM_METADATA: METADATA_SIMPLE,
    PARAM_SORT: SORT_ASCENDING,
    PARAM_FORMAT: FORMAT_JSON,
    PARAM_HEADER: HEADER_PARAM_NAMES,
    PARAM_DELIM: ',',
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


RESPONSE_ERROR_CODE = 400

COLLAPSE_AGG_NAME = 'agg'

CSV_RESPONSE_FILENAME = 'data.csv'


# Scripts de map reduce para calcular End of Period en Elasticsearch
EOP_INIT = """
params._agg.last_date = -1;
params._agg.value = 0;
"""

EOP_MAP = """
if (doc.timestamp.value > params._agg.last_date) {
    params._agg.last_date = doc.timestamp.value;
    params._agg.value = doc.value.value;
}
"""

EOP_REDUCE = """
double value = -1;
long last_date = 0;
for (a in params._aggs) {
    if (a != null && a.last_date > last_date && a.value != 0.0) {
        value = a.value;
        last_date = a.last_date;
        }
    }
return value
"""
