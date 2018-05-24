#! coding: utf-8
from django.conf import settings
from pandas.tseries.offsets import YearBegin, QuarterBegin, MonthBegin, Day


# Transformaciones
VALUE = 'value'
CHANGE = 'change'
PCT_CHANGE = 'percent_change'
CHANGE_YEAR_AGO = 'change_a_year_ago'
PCT_CHANGE_YEAR_AGO = 'percent_change_a_year_ago'

# Pandas freqs
PANDAS_YEAR = YearBegin()
PANDAS_SEMESTER = MonthBegin(6)
PANDAS_QUARTER = QuarterBegin(startingMonth=1)
PANDAS_MONTH = MonthBegin()
PANDAS_WEEK = Day(7)
PANDAS_DAY = Day()

# Frecuencias *en orden* de mayor a menor
PANDAS_FREQS = [PANDAS_YEAR, PANDAS_SEMESTER, PANDAS_QUARTER, PANDAS_MONTH, PANDAS_WEEK, PANDAS_DAY]

IDENTIFIER = "identifier"
DATASET_IDENTIFIER = "dataset_identifier"
DOWNLOAD_URL = "downloadURL"

DATASET = 'dataset'
DISTRIBUTION = 'distribution'
FIELD = 'field'
FIELD_TITLE = 'title'
FIELD_ID = 'id'
FIELD_DESCRIPTION = 'description'
SPECIAL_TYPE = 'specialType'
SPECIAL_TYPE_DETAIL = 'specialTypeDetail'
TIME_INDEX = 'time_index'

# JSON del mapping de series de tiempo
MAPPING = {
    "properties": {
        settings.TS_TIME_INDEX_FIELD: {"type": "date"},
        VALUE: {"type": "scaled_float", "scaling_factor": 10000000},
        CHANGE: {"type": "scaled_float", "scaling_factor": 10000000},
        PCT_CHANGE: {"type": "scaled_float", "scaling_factor": 10000000},
        CHANGE_YEAR_AGO: {"type": "scaled_float", "scaling_factor": 10000000},
        PCT_CHANGE_YEAR_AGO: {"type": "scaled_float", "scaling_factor": 10000000},
        "series_id": {"type": "keyword"},
        "aggregation": {"type": "keyword"},
        "interval": {"type": "keyword"},
        "raw_value": {"type": "boolean"},
    },
    "_all": {"enabled": False},
    "dynamic": "strict"
}


INDEX_CREATION_BODY = {
    'mappings': {
        settings.TS_DOC_TYPE: MAPPING
    }
}

FORCE_MERGE_SEGMENTS = 5

REQUEST_TIMEOUT = 30  # en segundos


# Frecuencias de pandas
DAILY_FREQ = 'D'
BUSINESS_DAILY_FREQ = 'B'

DEACTIVATE_REFRESH_BODY = {
    'index': {
        'refresh_interval': -1
    }
}

REACTIVATE_REFRESH_BODY = {
    'index': {
        'refresh_interval': "30s"
    }
}
