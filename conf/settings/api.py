#! coding: utf-8

# Default of docker container!
DEFAULT_ES_URL = "http://elastic:changeme@localhost:9200/"

# Único índice asignado a las series de tiempo
TS_INDEX = 'indicators'

# Índice para los test cases
TEST_INDEX = 'test_indicators'

# Único tipo asignado a las series de tiempo
TS_DOC_TYPE = "doc"

# Actualización de datos en segundos
TS_REFRESH_INTERVAL = "30s"

# Field del valor del índice de tiempo en ES
TS_TIME_INDEX_FIELD = 'timestamp'

# Nombre de la columna de índice de tiempo en las distribuciones
INDEX_COLUMN = 'indice_tiempo'

VALID_STATUS_CODES = (
    200,
    201
)

MAX_ALLOWED_VALUES = {
    'start': 100000,  # tbd
    'limit': 1000,
    'ids': 20  # Cantidad máxima de series que se pueden pedir
}


DISTRIBUTION_INDEX_JOB_TIMEOUT = 500  # Segundos

READ_DATAJSON_SHELL_CMD = 'read_datajson.sh'
