#! coding: utf-8

ELASTICSEARCH_ERROR = u"Error Fatal. Contacte un administrador"
SERIES_DOES_NOT_EXIST = u"Serie inexistente: {}"
INVALID_PARAMETER = u"Parámetro {} inválido: {}"
PARAMETER_OVER_LIMIT = u"Parámetro {} por encima del límite permitido ({}): {}"
INVALID_COLLAPSE = u"Intervalo de collapse inválido para la(s) serie(s) seleccionadas: {}. Pruebe con un intervalo mayor"
INVALID_DATE_FILTER = u"Filtro por rango temporal inválido (start > end)"
INVALID_DATE = u"Fecha de {} inválida (no ISO 8601): {}"
NO_TIME_SERIES_ERROR = u"No se especificó una serie de tiempo."
INVALID_SERIES_IDS_FORMAT = u"Formato de series a seleccionar inválido"
# Para el parámetro de IDS: rep mode ó agregación no reconocida
INVALID_TRANSFORMATION = u"Transformación inválida: {}"

SERIES_OVER_LIMIT = u"Cantidad de series pedidas por encima del límite permitido ({})"

EMPTY_QUERY_ERROR = u"Query vacía, primero agregue una serie"
INVALID_SORT_PARAMETER = u'"how" debe ser "asc", o "desc", recibido {}'

ES_NOT_INIT_ERROR = u"Instancia no inicializada. Pruebe con init(urls)"

INVALID_QUERY_TYPE = u"Este tipo de Query no soporta operaciones de collapse"

END_OF_PERIOD_ERROR = u"Agregación End of Period no soportada para series con índice menor a 1970"

INVALID_DELIM_LENGTH = u"El carácter delimitador debe ser uno sólo"
