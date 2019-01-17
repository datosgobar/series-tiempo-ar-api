from dateutil.relativedelta import relativedelta


def days_betwen(first_date, second_date):
    return (first_date - second_date).days


def weeks_between(first_date, second_date):
    return round((first_date - second_date).days / 7)


def months_between(first_date, second_date):
    if first_date.day != 1:
        first_date += relativedelta(months=1)

    delta = relativedelta(first_date, second_date)
    return delta.months + 12 * delta.years


def quarters_between(first_date, second_date):
    quarter_months = (1, 4, 7, 10)
    result = False
    if first_date.month not in quarter_months or (first_date.month in quarter_months and first_date.day != 1):
        result = True
    delta = relativedelta(first_date, second_date)
    return delta.months / 3 + 4 * delta.years + result


def semesters_between(first_date, second_date):
    semester_months = (1, 7)
    result = False
    if first_date.month not in semester_months or (first_date.month in semester_months and first_date.day != 1):
        result = True
    delta = relativedelta(first_date, second_date)
    return delta.months / 6 + 2 * delta.years + result


def years_between(first_date, second_date):
    if first_date.month != 1 or (first_date.month == 1 and first_date.day != 1):
        first_date += relativedelta(years=1)
    delta = relativedelta(first_date, second_date)

    return delta.years


def periods_between(first_date, second_date, periodicity):
    dispatcher = {
        'day': days_betwen,
        'week': weeks_between,
        'month': months_between,
        'quarter': quarters_between,
        'semester': semesters_between,
        'year': years_between,
    }

    return dispatcher[periodicity](first_date, second_date)
