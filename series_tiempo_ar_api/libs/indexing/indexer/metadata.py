#! coding: utf-8
import pandas as pd
from django_datajsonar.models import Field
from series_tiempo_ar_api.apps.management import meta_keys


def update_enhanced_meta(serie: pd.Series, catalog_id: str, distribution_id: str):
    """Crea o actualiza los metadatos enriquecidos de la serie pasada. El título de
    la misma DEBE ser el ID de la serie en la base de datos"""

    field = Field.objects.get(distribution__dataset__catalog__identifier=catalog_id,
                              distribution__identifier=distribution_id,
                              identifier=serie.name)
    periodicity = meta_keys.get(field.distribution, meta_keys.PERIODICITY)
    days_since_update = (pd.datetime.now() - _get_last_day_of_period(serie, periodicity)).days

    last = serie[-1]
    second_to_last = serie[-2] if serie.index.size > 1 else None
    last_pct_change = last / second_to_last - 1

    # Cálculos
    meta = {
        meta_keys.INDEX_START: serie.index.min().date(),
        meta_keys.INDEX_END: serie.index.max().date(),
        meta_keys.PERIODICITY: meta_keys.get(field.distribution, meta_keys.PERIODICITY),
        meta_keys.INDEX_SIZE: serie.index.size,
        meta_keys.DAYS_SINCE_LAST_UPDATE: days_since_update,
        meta_keys.LAST_VALUE: last,
        meta_keys.SECOND_TO_LAST_VALUE: second_to_last,
        meta_keys.LAST_PCT_CHANGE: last_pct_change,
    }

    for meta_key, value in meta.items():
        field.enhanced_meta.update_or_create(key=meta_key, defaults={'value': value})


def _get_last_day_of_period(serie: pd.Series, periodicity: str) -> int:
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
