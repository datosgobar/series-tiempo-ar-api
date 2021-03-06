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


def periodicity_human_format_to_iso(periodicity):
    periodicities = {
        'year': 'R/P1Y',
        'quarter': 'R/P3M',
        'month': 'R/P1M',
        'day': 'R/P1D',
        'semester': 'R/P6M'
    }
    return periodicities[periodicity]


def freq_pandas_to_index_offset(freq):
    """Dada una lista de datos de una serie de frecuencia 'freq',
    devuelve la distancia de elementos separados por un año en esa
    lista. Si no está definido (serie diaria o semanal), devuelve 0
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
    return 0


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


def get_periodicity_human_format_es(periodicity):
    periodicities = {
        'R/P1Y': 'anual',
        'R/P3M': 'trimestral',
        'R/P1M': 'mensual',
        'R/P1D': 'diaria',
        'R/P6M': 'semestral'
    }

    return periodicities[periodicity]


def extra_offset(periodicity):
    """Cantidad de valores extra a pedir en el offset de ES cuando se aplica
    la periodicidad pasada. Es necesario para que al aplicar transformaciones
    de variación, se devuelva la cantidad exacta esperada por el usuario.
    Ejemplo: limit=100, rep_mode=change_a_year_ago, devolvería 99 resultados
    en una serie anual, necesitamos sumar el valor devuelto por esta función
    """
    offsets = {
        'year': 1,
        'semester': 2,
        'quarter': 4,
        'month': 12,
        'day': 365,
    }
    return offsets.get(periodicity, 0)


def validate_positive_int(last: str) -> int:
    last = int(last)
    if last < 0:
        raise ValueError
    return last
