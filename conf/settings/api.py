#! coding: utf-8

ES_URL = "http://localhost:9200/"

# JSON string del mapping de los índices de series de tiempo
MAPPING = {
  "properties": {
    "timestamp":                    {"type": "date"},
    "value":                        {"type": "scaled_float", "scaling_factor": 10000000},
    "change":                       {"type": "scaled_float", "scaling_factor": 10000000},
    "percent_change":               {"type": "scaled_float", "scaling_factor": 10000000},
    "change_a_year_ago":            {"type": "scaled_float", "scaling_factor": 10000000},
    "percent_change_a_year_ago":    {"type": "scaled_float", "scaling_factor": 10000000}
  },
  "_all": {"enabled": False},
  "dynamic": "strict"
}

# Único índice asignado a las series de tiempo
TS_INDEX = 'indicators'

# Actualización de datos en segundos
TS_REFRESH_INTERVAL = "30s"

# Modos de representación de las series, calculados y guardados
# en el proceso de indexación
REP_MODES = [
    'value',
    'change',
    'change_a_year_ago',
    'percent_change',
    'percent_change_a_year_ago'
]

API_DEFAULT_VALUES = {
    'rep_mode': 'value',
    'collapse_aggregation': 'avg',
    'collapse': 'year',
    'start': 0,
    'limit': 100
}
