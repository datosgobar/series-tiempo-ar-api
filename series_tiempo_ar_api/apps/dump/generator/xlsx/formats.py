import math
from iso8601 import iso8601

from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.apps.dump.generator import constants as meta
from series_tiempo_ar_api.apps.dump.models import DumpFile


def value_format(val_str):
    if val_str:
        val = float(val_str)
        return val if math.isfinite(val) else ''
    return val_str


def date_format(date_str):
    if date_str:
        return iso8601.parse_date(date_str).date()
    return date_str


def int_format(int_str):
    if int_str:
        return int(int_str)
    return int_str


def bool_format(bool_str: str):
    bool_str = bool_str.lower()
    return True if bool_str == 'true' else False


formats = {
    DumpFile.FILENAME_FULL: {
        constants.FULL_CSV_HEADER.index('indice_tiempo'): date_format,
        constants.FULL_CSV_HEADER.index('valor'): value_format,
    },

    DumpFile.FILENAME_VALUES: {
        constants.VALUES_HEADER.index('indice_tiempo'): date_format,
        constants.VALUES_HEADER.index('valor'): value_format,
    },

    DumpFile.FILENAME_METADATA: {
        meta.METADATA_ROWS.index(meta.SERIES_INDEX_START): date_format,
        meta.METADATA_ROWS.index(meta.SERIES_INDEX_END): date_format,
        meta.METADATA_ROWS.index(meta.SERIES_LAST_VALUE): value_format,
        meta.METADATA_ROWS.index(meta.SERIES_SECOND_LAST_VALUE): value_format,
        meta.METADATA_ROWS.index(meta.SERIES_PCT_CHANGE): value_format,
        meta.METADATA_ROWS.index(meta.SERIES_VALUES_AMT): int_format,
        meta.METADATA_ROWS.index(meta.SERIES_DAYS_SINCE_LAST_UPDATE): int_format,
        meta.METADATA_ROWS.index(meta.SERIES_IS_UPDATED): bool_format,
    },

    DumpFile.FILENAME_SOURCES: {
        meta.SOURCES_ROWS.index(meta.SOURCE_SERIES_AMT): int_format,
        meta.SOURCES_ROWS.index(meta.SOURCE_VALUES_AMT): int_format,
        meta.SOURCES_ROWS.index(meta.SOURCE_FIRST_INDEX): date_format,
        meta.SOURCES_ROWS.index(meta.SOURCE_LAST_INDEX): date_format,
    }
}
