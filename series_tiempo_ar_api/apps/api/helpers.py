#! coding: utf-8
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


def freq_pandas_to_interval(freq):
    freqs = {
        'AS': 'year',
        'AS-JAN': 'year',
        '6MS': 'semester',
        '6MS-JAN': 'semester',
        'QS': 'quarter',
        'QS-JAN': 'quarter',
        'MS': 'month',
        '7D': 'week',
        'D': 'day'
    }

    return freqs[freq]


def interval_to_freq_pandas(freq):
    freqs = {
        'year': 'AS',
        'semester': '6MS',
        'quarter': 'QS',
        'month': 'MS',
        'week': '7D',
        'day': 'D'
    }

    return freqs[freq]


def get_relative_delta(periodicity):
    """Devuelve un objeto relativedelta a partir del intervalo
    'periodicity' pasado"""

    deltas = {
        'day': relativedelta(days=1),
        'week': relativedelta(days=7),
        'month': relativedelta(months=1),
        'quarter': relativedelta(months=3),
        'semester': relativedelta(months=6),
        'year': relativedelta(years=1)
    }

    return deltas[periodicity]
