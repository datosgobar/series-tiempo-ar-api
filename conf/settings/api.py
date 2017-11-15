#! coding: utf-8

# Default of docker container!
DEFAULT_ES_URL = "http://elastic:changeme@localhost:9200/"

# Único índice asignado a las series de tiempo
TS_INDEX = 'indicators'

# Único tipo asignado a las series de tiempo
TS_DOC_TYPE = "doc"

# Actualización de datos en segundos
TS_REFRESH_INTERVAL = "30s"

# Nombre de la columna de índice de tiempo en las distribuciones
INDEX_COLUMN = 'indice_tiempo'

VALID_STATUS_CODES = (
    200,
    201
)

MAX_ALLOWED_VALUES = {
    'start': 100000,  # tbd
    'limit': 1000
}
