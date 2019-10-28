from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from faker import Faker

from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.es_query.series import Serie


class SeriesStartOffsetTests(TestCase):

    def setUp(self):
        self.faker = Faker()

    def get_series(self, periodicity, rep_mode=None):
        fake_index = self.faker.pystr().lower()
        series_id = self.faker.pystr()
        rep_mode = rep_mode or constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE]
        return Serie(index=fake_index,
                     series_id=series_id,
                     rep_mode=rep_mode,
                     periodicity=periodicity)

    def test_series_id_same_start(self):
        one_series = self.get_series('month')
        other_series = self.get_series('month')

        start_date = datetime(2016, 1, 1)
        start = one_series.get_es_start({one_series.series_id: start_date, other_series.series_id: start_date}, 0)

        self.assertEqual(start, 0)

    def test_series_id_one_month_earlier_start(self):
        one_series = self.get_series('month')
        other_series = self.get_series('month')

        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(months=1)
        start_dates = {one_series.series_id: one_start_date,
                       other_series.series_id: other_start_date}

        start = one_series.get_es_start(start_dates, 1)
        other_start = other_series.get_es_start(start_dates, 1)
        self.assertEqual(start, 1)
        self.assertEqual(other_start, 0)

    def test_series_with_collapse(self):
        one_series = self.get_series('month')
        other_series = self.get_series('month')

        one_series.add_collapse('year')
        other_series.add_collapse('year')

        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(months=1)
        start_dates = {one_series.series_id: one_start_date,
                       other_series.series_id: other_start_date}

        start = one_series.get_es_start(start_dates, 1)
        other_start = other_series.get_es_start(start_dates, 1)
        self.assertEqual(start, 1)
        self.assertEqual(other_start, 0)

    def test_series_different_periodicity(self):
        one_series = self.get_series('year')
        other_series = self.get_series('month')

        other_series.add_collapse('year')

        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(months=1)
        start_dates = {one_series.series_id: one_start_date,
                       other_series.series_id: other_start_date}

        start = one_series.get_es_start(start_dates, 1)
        other_start = other_series.get_es_start(start_dates, 1)
        self.assertEqual(start, 1)
        self.assertEqual(other_start, 0)

    def test_series_start_many_years_delay(self):
        one_series = self.get_series('year')
        other_series = self.get_series('year')

        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(years=100)
        start_dates = {one_series.series_id: one_start_date,
                       other_series.series_id: other_start_date}

        start = one_series.get_es_start(start_dates, 50)
        other_start = other_series.get_es_start(start_dates, 50)
        self.assertEqual(start, 50)
        self.assertEqual(other_start, 0)

    def test_series_day_and_month_periodicity(self):
        one_series = self.get_series('month')
        other_series = self.get_series('day')

        other_series.add_collapse('month')
        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(days=1)

        start_dates = {one_series.series_id: one_start_date,
                       other_series.series_id: other_start_date}

        start = one_series.get_es_start(start_dates, 50)
        other_start = other_series.get_es_start(start_dates, 50)

        self.assertEqual(start, 50)
        self.assertEqual(other_start, 49)

    def test_series_day_and_quarter_periodicity(self):
        one_series = self.get_series('quarter')
        other_series = self.get_series('day')

        other_series.add_collapse('quarter')
        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(days=1)

        start_dates = {one_series.series_id: one_start_date,
                       other_series.series_id: other_start_date}

        start = one_series.get_es_start(start_dates, 50)
        other_start = other_series.get_es_start(start_dates, 50)

        self.assertEqual(start, 50)
        self.assertEqual(other_start, 49)

    def test_series_day_and_semester_periodicity(self):
        one_series = self.get_series('semester')
        other_series = self.get_series('day')

        other_series.add_collapse('semester')
        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(days=1)

        start_dates = {one_series.series_id: one_start_date,
                       other_series.series_id: other_start_date}

        start = one_series.get_es_start(start_dates, 50)
        other_start = other_series.get_es_start(start_dates, 50)

        self.assertEqual(start, 50)
        self.assertEqual(other_start, 49)
