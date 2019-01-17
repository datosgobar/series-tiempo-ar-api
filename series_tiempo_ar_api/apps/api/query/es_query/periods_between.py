from dateutil.relativedelta import relativedelta


def days_between(first_date, second_date):
    return (first_date - second_date).days


def weeks_between(first_date, second_date):
    return round(days_between(first_date, second_date) / 7)


def months_between(first_date, second_date):
    if first_date.day != 1:
        first_date += relativedelta(months=1)

    delta = relativedelta(first_date, second_date)
    return delta.months + 12 * delta.years


def quarters_between(first_date, second_date):
    period_start_extra = 0 if is_period_start(first_date, (1, 4, 7, 10)) else 1
    delta = relativedelta(first_date, second_date)
    return delta.months / 3 + 4 * delta.years + period_start_extra


def semesters_between(first_date, second_date):
    period_start_extra = 0 if is_period_start(first_date, (1, 7)) else 1
    delta = relativedelta(first_date, second_date)
    return delta.months / 6 + 2 * delta.years + period_start_extra


def years_between(first_date, second_date):
    period_start_extra = 0 if is_period_start(first_date, (1, )) else 1
    delta = relativedelta(first_date, second_date)

    return delta.years + period_start_extra


def periods_between(first_date, second_date, periodicity):
    dispatcher = {
        'day': days_between,
        'week': weeks_between,
        'month': months_between,
        'quarter': quarters_between,
        'semester': semesters_between,
        'year': years_between,
    }

    return dispatcher[periodicity](first_date, second_date)


def is_period_start(date, period_start_months):
    """Se considera una fecha como comienzo de un período si su día es 1, y su mes es
    igual al de un período. Para mensual son todos los meses válidos, para trimestral,
    Enero, Abril, Julio, Octubre, para semestral Enero y Julio, para anual, sólo Enero
    """
    if date.month not in period_start_months:
        return False

    if date.day != 1:
        return False

    return True
