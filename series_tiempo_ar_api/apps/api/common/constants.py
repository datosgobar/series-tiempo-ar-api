from pandas.tseries.offsets import YearBegin, QuarterBegin, MonthBegin, Day


# Transformaciones
VALUE = 'value'
CHANGE = 'change'
PCT_CHANGE = 'percent_change'
CHANGE_YEAR_AGO = 'change_a_year_ago'
PCT_CHANGE_YEAR_AGO = 'percent_change_a_year_ago'

# Pandas freqs
PANDAS_YEAR = YearBegin()
PANDAS_QUARTER = QuarterBegin(startingMonth=1)
PANDAS_MONTH = MonthBegin()
PANDAS_WEEK = Day(7)
PANDAS_DAY = Day()

PANDAS_FREQS = [PANDAS_YEAR, PANDAS_QUARTER, PANDAS_MONTH, PANDAS_WEEK, PANDAS_DAY]
