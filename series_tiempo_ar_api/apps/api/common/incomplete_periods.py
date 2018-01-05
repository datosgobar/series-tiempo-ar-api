#! coding: utf-8
from calendar import monthrange

from dateutil.relativedelta import relativedelta

from series_tiempo_ar_api.apps.api.common import constants


def handle_missing_values(col, result_col):
    handle_last_value(col, result_col.index.freq, result_col)


def handle_last_value(col, target_freq, result_col):
    """Borra el último valor a indexar si este no cumple con un intervalo completo de collapse
    Se considera intervalo completo al que tenga todos los valores posibles del intervalo
    target, ej: un collapse mensual -> anual debe tener valores para los 12 meses del año
    """
    handlers = {
        constants.PANDAS_SEMESTER: {
            constants.PANDAS_YEAR: handle_semester_year
        },
        constants.PANDAS_QUARTER: {
            constants.PANDAS_YEAR: handle_quarter_year,
            constants.PANDAS_SEMESTER: handle_quarter_semester
        },
        constants.PANDAS_MONTH: {
            constants.PANDAS_YEAR: handle_month_year,
            constants.PANDAS_SEMESTER: handle_month_semester,
            constants.PANDAS_QUARTER: handle_month_quarter,
        },
        constants.PANDAS_DAY: {
            constants.PANDAS_YEAR: handle_day_year,
            constants.PANDAS_SEMESTER: handle_day_semester,
            constants.PANDAS_QUARTER: handle_day_quarter,
            constants.PANDAS_MONTH: handle_day_month,
        },
    }
    orig_freq = col.index.freq
    # Si no hay handler, no hacemos nada
    if orig_freq not in handlers.keys() or target_freq not in handlers[orig_freq].keys():
        return

    orig_first_date = col.index[0]
    orig_last_date = col.index[-1]
    result_first_date = result_col.index[0]
    result_last_date = result_col.index[-1]
    handlers[orig_freq][target_freq](result_col,
                                     orig_first_date,
                                     orig_last_date,
                                     result_first_date,
                                     result_last_date)


def handle_semester_year(result, orig_first_date, orig_last_date, *_):
    # Colapso semester -> year: debe estar presente el último semestre (mes 7)
    if orig_last_date.month != 7:
        handle_incomplete_value(result)

    # Para el primer año debe estar presente el primer semestre (mes 1)
    if orig_first_date.month != 1:
        handle_incomplete_value(result, which='first')


def handle_quarter_year(result, orig_first_date, orig_last_date, *_):

    # Colapso quarter -> year: debe estar presente el último quarter (mes 10)
    if orig_last_date.month != 10:
        handle_incomplete_value(result)

    # Para el primer año debe estar presente desde el primer quarter (mes 1)
    if orig_first_date.month != 1:
        handle_incomplete_value(result, which='first')


def handle_quarter_semester(result, orig_first_date, orig_last_date, result_first_date, result_last_date):
    if (result_last_date.month == 1 and orig_last_date.quarter != 2) or \
            (result_last_date.month == 7 and orig_last_date.quarter != 4):
        handle_incomplete_value(result)

    if (result_first_date.month == 1 and orig_first_date.quarter != 1) or \
            (result_first_date.month == 7 and orig_first_date.quarter != 3):
        handle_incomplete_value(result, which='first')


def handle_month_year(result, orig_first_date, orig_last_date, *_):

    if orig_last_date.month != 12:
        handle_incomplete_value(result)

    if orig_first_date.month != 1:
        handle_incomplete_value(result, which='first')


def handle_month_semester(result, orig_first_date, orig_last_date, result_first_date, result_last_date):
    if (result_last_date.month == 1 and orig_last_date.month != 6) or \
            (result_last_date.month == 7 and orig_last_date.month != 12):
        handle_incomplete_value(result)

    if result_first_date.month != orig_first_date.month:
        handle_incomplete_value(result, which='first')


def handle_month_quarter(result, orig_first_date, orig_last_date, result_first_date, result_last_date):

    # Colapso month -> quarter: debe estar presente el último mes del quarter
    # Ese mes se puede calcular como quarter * 3 (03, 06, 09, 12)
    if orig_last_date.month != result_last_date.quarter * 3:
        handle_incomplete_value(result)

    # Primer mes debe ser el primero del quarter
    # Es equivalente a quarter * 3 - 2 (meses 01, 04, 07, 10)
    if orig_first_date.month != result_first_date.quarter * 3 - 2:
        handle_incomplete_value(result, which='first')


def handle_day_year(result, orig_first_date, orig_last_date, *_):
    # Colapso day -> year: debe haber valores hasta el 12-31
    if orig_last_date.month != 12 or orig_last_date.day != 31:
        handle_incomplete_value(result)

    # Primer día debe ser 01/01
    if orig_first_date.month != 1 or orig_first_date.day != 1:
        handle_incomplete_value(result, which='first')


def handle_day_semester(result, orig_first_date, orig_last_date, result_first_date, result_last_date):
    last_date_prev_month = result_last_date - relativedelta(months=1)
    _, last_day = monthrange(last_date_prev_month.year, last_date_prev_month.month)
    if last_date_prev_month.month != orig_last_date.month or last_day != orig_last_date.day:
        handle_incomplete_value(result)

    # Primer día debe ser el primero del semestre (01-01 o 07-01)
    if (orig_first_date.month != result_first_date.month or
            orig_first_date.day != result_first_date.day):
        handle_incomplete_value(result, which='first')


def handle_day_quarter(result, orig_first_date, orig_last_date, result_first_date, result_last_date):
    # Colapso day -> quarter: debe haber valores hasta 31/03, 30/06, 30/09 o 31/12
    # El último mes del quarter se puede calcular como quarter * 3
    _, last_day = monthrange(result_last_date.year, result_last_date.quarter * 3)
    if orig_last_date.day != last_day or orig_last_date.month != result_last_date.quarter * 3:
        handle_incomplete_value(result)

    # Primer día debe ser el primero del quarter (01-01, 04-01, 07-01, 10-01)
    if (orig_first_date.month != result_first_date.month or
            orig_first_date.day != result_first_date.day):
        handle_incomplete_value(result, which='first')


def handle_day_month(result, orig_first_date, orig_last_date, result_first_date, result_last_date):
    # Colapso day -> month: debe haber valores hasta el último día del mes
    _, last_day = monthrange(result_last_date.year, result_last_date.month)
    if result_last_date.month != result_last_date.month or orig_last_date.day != last_day:
        handle_incomplete_value(result)

    # Primer día debe ser el primero del mes
    if (orig_first_date.month != result_first_date.month or
            orig_first_date.day != result_first_date.day):
        handle_incomplete_value(result, which='first')


def handle_incomplete_value(col, which='last'):
    if which not in ('first', 'last'):
        raise ValueError

    idx = -1 if which == 'last' else 0
    del col[col.index[idx]]
