#! coding: utf-8

"""Operaciones de cálculos de variaciones absolutas y porcentuales anuales"""

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

from series_tiempo_ar_api.apps.api.helpers import freq_pandas_to_index_offset


def get_value(df, col, index):
    """Devuelve el valor del df[col][index] o 0 si no es válido.
    Evita Cargar Infinity y NaN en Elasticsearch
    """
    series = df[col]
    if index not in series:
        return 0

    value = series[index]
    return value if np.isfinite(value) else 0


def year_ago_column(col, freq, operation):
    """Aplica operación entre los datos de una columna y su valor
    un año antes. Devuelve una nueva serie de pandas.
    """
    array = []
    offset = freq_pandas_to_index_offset(freq) or 0
    if offset:
        values = col.values
        array = operation(values[offset:], values[:-offset])
    else:
        for idx, val in col.iteritems():
            value = get_value_a_year_ago(idx, col, validate=True)
            if value != 0:
                array.append(operation(val, value))
            else:
                array.append(None)

    return pd.Series(array, index=col.index[offset:])


def get_value_a_year_ago(idx, col, validate=False):
    """Devuelve el valor de la serie determinada por df[col] un
    año antes del índice de tiempo 'idx'. Hace validación de si
    existe el índice o no según 'validate' (operación costosa)
    """

    value = 0
    year_ago_idx = idx.date() - relativedelta(years=1)
    if not validate:
        if year_ago_idx not in col.index:
            return 0

        value = col[year_ago_idx]
    else:
        if year_ago_idx in col:
            value = col[year_ago_idx]

    return value


def change_a_year_ago(col, freq):
    def change(x, y):
        return x - y
    return year_ago_column(col, freq, change)


def pct_change_a_year_ago(col, freq):
    def _pct_change(x, y):
        if isinstance(y, int) and y == 0:
            return 0
        return (x - y) / y

    return year_ago_column(col, freq, _pct_change)
