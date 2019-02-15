from series_tiempo_ar_api.libs.indexing.constants import \
    VALUE, CHANGE, PCT_CHANGE, CHANGE_YEAR_AGO, PCT_CHANGE_YEAR_AGO


SERIES_QUERY_INDEX_NAME = 'query'


REP_MODES = [
    VALUE,
    CHANGE,
    PCT_CHANGE,
    CHANGE_YEAR_AGO,
    PCT_CHANGE_YEAR_AGO,
]

AGG_DEFAULT = 'avg'
AGG_SUM = 'sum'
AGG_END_OF_PERIOD = 'end_of_period'
AGG_MAX = 'max'
AGG_MIN = 'min'
AGGREGATIONS = [
    AGG_DEFAULT,
    AGG_SUM,
    AGG_END_OF_PERIOD,
    AGG_MAX,
    AGG_MIN,
]

PARAM_REP_MODE = 'representation_mode'
PARAM_COLLAPSE_AGG = 'collapse_aggregation'
