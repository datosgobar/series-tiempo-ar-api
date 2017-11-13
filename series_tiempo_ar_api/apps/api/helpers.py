#! coding: utf-8
from django.conf import settings
from dateutil.relativedelta import relativedelta


def get_periodicity_human_format(periodicity):
    periodicities = {
        'R/P1Y': 'year',
        'R/P3M': 'quarter',
        'R/P1M': 'month',
        'R/P1D': 'day',
        'R/P6M': 'semester'
    }

    return periodicities[periodicity]


def freq_pandas_to_index_offset(freq):
    """Dada una lista de datos de una serie de frecuencia 'freq',
    devuelve el la distancia de elementos separados por un año en esa
    lista.
    Ejemplo: para una serie mensual se devuelve 12
    """
    offset = {
        'AS': 1,
        '6MS': 2,
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


def find_index(list_of_lists, element):
    """Devuelve el índice de la lista que contenga la primera
    ocurrencia de 'element' en la lista de listas. Si no se encuentra
    ninguna devuelve -1
    """
    for i, row in enumerate(list_of_lists):
        if element in row:
            return i
    return -1


def get_relative_delta(periodicity):
    """Devuelve un objeto relativedelta a partir del intervalo
    'periodicity' pasado"""

    deltas = {
        'day': relativedelta(days=1),
        'month': relativedelta(months=1),
        'quarter': relativedelta(months=3),
        'year': relativedelta(years=1)
    }

    return deltas[periodicity]
