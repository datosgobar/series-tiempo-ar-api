#! coding: utf-8
from datetime import datetime
import pandas as pd
from pydatajson.helpers import parse_repeating_time_interval_to_days
from django_datajsonar.models import Field
from series_tiempo_ar_api.apps.management import meta_keys


def update_enhanced_meta(serie: pd.Series, catalog_id: str, distribution_id: str):
    """Crea o actualiza los metadatos enriquecidos de la serie pasada. El título de
    la misma DEBE ser el ID de la serie en la base de datos"""

    field = Field.objects.get(distribution__dataset__catalog__identifier=catalog_id,
                              distribution__identifier=distribution_id,
                              identifier=serie.name)
    periodicity = meta_keys.get(field.distribution, meta_keys.PERIODICITY)
    days_since_update = (datetime.now() - _get_last_day_of_period(serie, periodicity)).days

    last = serie[-1]
    second_to_last = serie[-2] if serie.index.size > 1 else None
    last_pct_change = last / second_to_last - 1

    # Cálculos
    meta = {
        meta_keys.INDEX_START: serie.first_valid_index().date(),
        meta_keys.INDEX_END: serie.last_valid_index().date(),
        meta_keys.PERIODICITY: periodicity,
        meta_keys.INDEX_SIZE: _get_index_size(serie),
        meta_keys.DAYS_SINCE_LAST_UPDATE: days_since_update,
        meta_keys.LAST_VALUE: last,
        meta_keys.SECOND_TO_LAST_VALUE: second_to_last,
        meta_keys.LAST_PCT_CHANGE: last_pct_change,
        meta_keys.IS_UPDATED: _is_series_updated(days_since_update, periodicity)
    }

    for meta_key, value in meta.items():
        field.enhanced_meta.update_or_create(key=meta_key, defaults={'value': value})


def _get_last_day_of_period(serie: pd.Series, periodicity: str) -> pd.datetime:
    frequencies_map_end = {
        "R/P1Y": "A",
        "R/P6M": "6M",
        "R/P3M": "Q",
        "R/P1M": "M",
        "R/P1D": "D"
    }
    period = pd.to_datetime(serie.index.max()).to_period(frequencies_map_end[periodicity])
    last_day = period.to_timestamp(how='end')
    return last_day


def _get_index_size(serie: pd.Series):
    # Filtro los NaN antes y después de la serie
    return len(serie[serie.first_valid_index():serie.last_valid_index()])


def _is_series_updated(days_since_last_update, periodicity):
    period_days = parse_repeating_time_interval_to_days(periodicity)
    periods_tolerance = {
        "R/P1Y": 2,
        "R/P6M": 2,
        "R/P3M": 2,
        "R/P1M": 3,
        "R/P1D": 14
    }
    days_tolerance = periods_tolerance.get(periodicity, 2) * period_days
    return days_since_last_update < days_tolerance
