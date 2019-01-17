from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.es_query.series import Series
from faker import Faker


class SeriesStartOffsetTests(TestCase):

    def setUp(self):
        self.faker = Faker()

    def get_serie(self, periodicity, rep_mode=None):
        fake_index = self.faker.pystr().lower()
        serie_id = self.faker.pystr()
        rep_mode = rep_mode or constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE]
        return Series(index=fake_index,
                      series_id=serie_id,
                      rep_mode=rep_mode,
                      periodicity=periodicity)

    def test_series_id_same_start(self):
        one_serie = self.get_serie('month')
        other_serie = self.get_serie('month')

        start_date = datetime(2016, 1, 1)
        start = one_serie.get_es_start({one_serie.series_id: start_date, other_serie.series_id: start_date}, 0)

        self.assertEqual(start, 0)

    def test_series_id_one_month_earlier_start(self):
        one_serie = self.get_serie('month')
        other_serie = self.get_serie('month')

        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(months=1)
        start_dates = {one_serie.series_id: one_start_date,
                       other_serie.series_id: other_start_date}

        start = one_serie.get_es_start(start_dates, 1)
        other_start = other_serie.get_es_start(start_dates, 1)
        self.assertEqual(start, 1)
        self.assertEqual(other_start, 0)

    def test_series_with_collapse(self):
        one_serie = self.get_serie('month')
        other_serie = self.get_serie('month')

        one_serie.add_collapse('year')
        other_serie.add_collapse('year')

        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(months=1)
        start_dates = {one_serie.series_id: one_start_date,
                       other_serie.series_id: other_start_date}

        start = one_serie.get_es_start(start_dates, 1)
        other_start = other_serie.get_es_start(start_dates, 1)
        self.assertEqual(start, 1)
        self.assertEqual(other_start, 0)

    def test_series_different_periodicity(self):
        one_serie = self.get_serie('year')
        other_serie = self.get_serie('month')

        other_serie.add_collapse('year')

        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(months=1)
        start_dates = {one_serie.series_id: one_start_date,
                       other_serie.series_id: other_start_date}

        start = one_serie.get_es_start(start_dates, 1)
        other_start = other_serie.get_es_start(start_dates, 1)
        self.assertEqual(start, 1)
        self.assertEqual(other_start, 0)

    def test_series_start_many_years_delay(self):
        one_serie = self.get_serie('year')
        other_serie = self.get_serie('year')

        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(years=100)
        start_dates = {one_serie.series_id: one_start_date,
                       other_serie.series_id: other_start_date}

        start = one_serie.get_es_start(start_dates, 50)
        other_start = other_serie.get_es_start(start_dates, 50)
        self.assertEqual(start, 50)
        self.assertEqual(other_start, 0)

    def test_series_day_and_month_periodicity(self):
        one_serie = self.get_serie('month')
        other_serie = self.get_serie('day')

        other_serie.add_collapse('month')
        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(days=1)

        start_dates = {one_serie.series_id: one_start_date,
                       other_serie.series_id: other_start_date}

        start = one_serie.get_es_start(start_dates, 50)
        other_start = other_serie.get_es_start(start_dates, 50)

        self.assertEqual(start, 50)
        self.assertEqual(other_start, 49)

    def test_series_day_and_quarter_periodicity(self):
        one_serie = self.get_serie('quarter')
        other_serie = self.get_serie('day')

        other_serie.add_collapse('quarter')
        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(days=1)

        start_dates = {one_serie.series_id: one_start_date,
                       other_serie.series_id: other_start_date}

        start = one_serie.get_es_start(start_dates, 50)
        other_start = other_serie.get_es_start(start_dates, 50)

        self.assertEqual(start, 50)
        self.assertEqual(other_start, 49)

    def test_series_day_and_semester_periodicity(self):
        one_serie = self.get_serie('semester')
        other_serie = self.get_serie('day')

        other_serie.add_collapse('semester')
        one_start_date = datetime(2016, 1, 1)
        other_start_date = one_start_date + relativedelta(days=1)

        start_dates = {one_serie.series_id: one_start_date,
                       other_serie.series_id: other_start_date}

        start = one_serie.get_es_start(start_dates, 50)
        other_start = other_serie.get_es_start(start_dates, 50)

        self.assertEqual(start, 50)
        self.assertEqual(other_start, 49)
