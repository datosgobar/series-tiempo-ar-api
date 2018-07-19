#!coding=utf8
"""Keys para usar junto con los campos de enhanced_meta que provee django datajsonar"""

AVAILABLE = 'available'
PERIODICITY = 'periodicity'
CHANGED = 'changed'
LAST_HASH = 'last_hash'
ERROR_MSG = 'error_msg'

INDEX_START = 'index_start'
INDEX_END = 'index_end'
INDEX_SIZE = 'index_size'
DAYS_SINCE_LAST_UPDATE = 'days_since_last_update'
LAST_VALUE = 'last_value'
SECOND_TO_LAST_VALUE = 'second_to_last_value'
LAST_PCT_CHANGE = 'last_pct_change'


def get(model, key):
    values = model.enhanced_meta.filter(key=key).values_list('value', flat=True)

    if values:
        return values[0]
    return None
