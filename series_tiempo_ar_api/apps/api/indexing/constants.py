#! coding: utf-8

IDENTIFIER = "identifier"
DATASET_IDENTIFIER = "dataset_identifier"
DOWNLOAD_URL = "downloadURL"

DATASET = 'dataset'
DISTRIBUTION = 'distribution'
FIELD = 'field'
FIELD_TITLE = 'title'
FIELD_ID = 'id'
SPECIAL_TYPE = 'specialType'
SPECIAL_TYPE_DETAIL = 'specialTypeDetail'
TIME_INDEX = 'time_index'


VALUE = 'value'
CHANGE = 'change'
PCT_CHANGE = 'percent_change'
CHANGE_YEAR_AGO = 'change_a_year_ago'
PCT_CHANGE_YEAR_AGO = 'percent_change_a_year_ago'

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
