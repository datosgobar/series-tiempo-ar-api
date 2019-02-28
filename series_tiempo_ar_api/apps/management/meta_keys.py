#!coding=utf8
"""Keys para usar junto con los campos de enhanced_meta que provee django datajsonar"""
from typing import Optional

AVAILABLE = 'available'
PERIODICITY = 'frequency'
CHANGED = 'changed'
LAST_HASH = 'last_hash'

INDEX_START = 'time_index_start'
INDEX_END = 'time_index_end'
INDEX_SIZE = 'time_index_size'
DAYS_SINCE_LAST_UPDATE = 'days_without_data'
LAST_VALUE = 'last_value'
SECOND_TO_LAST_VALUE = 'second_to_last_value'
LAST_PCT_CHANGE = 'last_pct_change'
IS_UPDATED = 'is_updated'

AVERAGE = 'average'
MAX = 'max_value'
MIN = 'min_value'

HITS_TOTAL = 'hits_total'
HITS_30_DAYS = 'hits_30_days'
HITS_90_DAYS = 'hits_90_days'
HITS_180_DAYS = 'hits_180_days'

HITS_KEYS = (HITS_180_DAYS, HITS_90_DAYS, HITS_30_DAYS, HITS_TOTAL)


def get(model, key) -> Optional[str]:
    values = model.enhanced_meta.filter(key=key).values_list('value', flat=True)

    if values:
        return values[0]
    return None
