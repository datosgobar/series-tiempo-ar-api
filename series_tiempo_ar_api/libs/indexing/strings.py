#! coding: utf-8
READ_ERROR = u"Error en la lectura del catálogo {}: {}"

PIPELINE_START = u"Comienzo de la indexación del catálogo %s"

# Scraping
START_SCRAPING = u"Comienzo del scraping"
END_SCRAPING = u"Fin del scraping"
INVALID_DISTRIBUTION_URL = u"URL inválida en distribución {}"
DESESTIMATED_DISTRIBUTION = u"Desestimada la distribución"

NO_SERIES_SCRAPPED = u"No fueron encontradas series de tiempo en este catálogo"

# Database Loader
DB_LOAD_START = u"Comienzo de la escritura a base de datos"
DB_LOAD_END = u"Fin de la escritura a base de datos"
DB_SERIES_ID_REPEATED = u"Serie ID {} en el catálogo {} ya existente. Desestimado"

# Indexer
INDEX_START = u"Inicio de la indexación"
INDEX_END = u"Fin de la indexación"
BULK_REQUEST_START = u"Inicio del bulk request a ES"
BULK_REQUEST_END = u"Fin del bulk request a ES"


SERIES_NOT_FOUND = u"Serie %s no encontrada en su dataframe"
BULK_REQUEST_ERROR = u"Error en la indexación: %s"
