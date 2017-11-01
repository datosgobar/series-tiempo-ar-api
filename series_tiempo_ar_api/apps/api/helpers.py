#! coding: utf-8


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
