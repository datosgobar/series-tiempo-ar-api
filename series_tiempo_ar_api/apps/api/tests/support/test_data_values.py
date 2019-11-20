from datetime import datetime

from dateutil.relativedelta import relativedelta

START_DATE = datetime(1999, 1, 1)
END_DATE = START_DATE + relativedelta(years=10)
START_VALUE = 100
