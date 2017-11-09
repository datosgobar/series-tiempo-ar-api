#! coding: utf-8
from django.conf import settings


def get_periodicity_human_format(periodicity):
    periodicities = {
        'R/P1Y': 'year',
        'R/P3M': 'quarter',
        'R/P1M': 'month',
        'R/P1D': 'day'
    }

    return periodicities[periodicity]


def freq_pandas_to_index_offset(freq):
    offset = {
        'AS': 1,
        'QS': 4,
        'MS': 12
    }
    for key, value in offset.items():
        if key in freq:
            return value


def get_max_periodicity(periodicities):
    """Devuelve la periodicity máxima en la lista periodicities,
    en formato 'humano' y legible por Elasticsearch (no ISO 8601)
    """
    order = settings.COLLAPSE_INTERVALS
    index = 0
    for periodicity in periodicities:
        field_index = order.index(get_periodicity_human_format(periodicity))
        index = index if index > field_index else field_index

    return order[index]
