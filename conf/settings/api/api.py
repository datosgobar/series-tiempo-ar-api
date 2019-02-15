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

MAX_SERIES_VALUES = 100000
MAX_LIMIT = 5000

MAX_ALLOWED_VALUES = {
    'start': MAX_SERIES_VALUES - MAX_LIMIT,  # Offset máximo
    'limit': MAX_LIMIT,  # Tamaño de página
    'ids': 40,  # Cantidad máxima de series que se pueden pedir
    'last': MAX_LIMIT,
}


DISTRIBUTION_INDEX_JOB_TIMEOUT = 1000  # Segundos

# Nombre del grupo de usuarios que reciben reportes de indexación
READ_DATAJSON_RECIPIENT_GROUP = 'read_datajson_recipients'

# Nombre del grupo de usuarios que reciben reportes de errores en tests de integración
INTEGRATION_TEST_REPORT_GROUP = 'integration_test_recipients'

# Metadata blacklists
CATALOG_BLACKLIST = [
    "themeTaxonomy"
]

DATASET_BLACKLIST = [

]

DISTRIBUTION_BLACKLIST = [
    "scrapingFileSheet"
]

FIELD_BLACKLIST = [
    "scrapingDataStartCell",
    "scrapingIdentifierCell",
    "scrapingDataStartCell",
]
