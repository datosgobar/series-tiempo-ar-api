#! coding: utf-8

# Default of docker container!
DEFAULT_ES_URL = "http://elastic:changeme@localhost:9200/"

# JSON del mapping de series de tiempo
MAPPING = {
  "properties": {
    "timestamp":                    {"type": "date"},
    "value":                        {"type": "scaled_float", "scaling_factor": 10000000},
    "change":                       {"type": "scaled_float", "scaling_factor": 10000000},
    "percent_change":               {"type": "scaled_float", "scaling_factor": 10000000},
    "change_a_year_ago":            {"type": "scaled_float", "scaling_factor": 10000000},
    "percent_change_a_year_ago":    {"type": "scaled_float", "scaling_factor": 10000000},
    "series_id":                    {"type": "keyword"}
  },
  "_all": {"enabled": False},
  "dynamic": "strict"
}

# Único índice asignado a las series de tiempo
TS_INDEX = 'indicators'

# Único tipo asignado a las series de tiempo
TS_DOC_TYPE = "doc"

INDEX_CREATION_BODY = {
    'mappings': {
        TS_DOC_TYPE: MAPPING
    }
}

# Actualización de datos en segundos
TS_REFRESH_INTERVAL = "30s"


# Nombre de la columna de índice de tiempo en las distribuciones
INDEX_COLUMN = 'indice_tiempo'

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


VALID_STATUS_CODES = (
    200,
    201
)

FORCE_MERGE_SEGMENTS = 5

REQUEST_TIMEOUT = 30  # en segundos

MAX_ALLOWED_VALUE = {
    'start': 100000,  # tbd
    'limit': 1000
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
