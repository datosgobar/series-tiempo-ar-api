#! coding: utf-8

import pandas as pd
from django.test import TestCase
from random import random

from nose.tools import raises

from series_tiempo_ar_api.libs.indexing import constants
from series_tiempo_ar_api.libs.indexing.incomplete_periods import \
    handle_missing_values, handle_incomplete_value


class IncompletePeriodsTests(TestCase):
    length = 400

    start_date = "2000-02-01"

    def setUp(self):
        self.col = pd.Series([random() for _ in range(self.length)])

    def init_series(self, start_date, freq, target_freq):
        idx = pd.DatetimeIndex(start=start_date, freq=freq,
                               periods=self.length)
        self.col.index = idx
        transform_col = self.col.resample(target_freq).mean()

        # Fix a colapsos fuera de fase:
        if target_freq == constants.PANDAS_SEMESTER:
            months_offset = transform_col.index[0].month - 1
            if months_offset:
                transform_col.drop(transform_col.index[0], inplace=True)
            offset = pd.DateOffset(months=months_offset)
            transform_col.index = transform_col.index - offset
            transform_col.index.freq = constants.PANDAS_SEMESTER

        return transform_col

    def test_handle_semester_year(self):
        transform_col = self.init_series("2000-02-01",
                                         constants.PANDAS_SEMESTER,
                                         constants.PANDAS_YEAR)

        prev_length = len(transform_col)
        handle_missing_values(self.col, transform_col)
        self.assertEqual(len(transform_col), prev_length - 2)

    def test_handle_quarter_year(self):
        transform_col = self.init_series("2000-02-01",
                                         constants.PANDAS_QUARTER,
                                         constants.PANDAS_YEAR)

        prev_length = len(transform_col)
        handle_missing_values(self.col, transform_col)
        self.assertEqual(len(transform_col), prev_length - 2)

    def test_handle_quarter_semester(self):
        transform_col = self.init_series("2000-04-01",
                                         constants.PANDAS_QUARTER,
                                         constants.PANDAS_SEMESTER)

        prev_length = len(transform_col)
        handle_missing_values(self.col, transform_col)
        self.assertEqual(len(transform_col), prev_length - 2)

    def test_handle_month_year(self):
        transform_col = self.init_series("2000-04-01",
                                         constants.PANDAS_MONTH,
                                         constants.PANDAS_YEAR)

        prev_length = len(transform_col)
        handle_missing_values(self.col, transform_col)
        self.assertEqual(len(transform_col), prev_length - 2)

    def test_handle_month_semester(self):
        transform_col = self.init_series("2000-06-01",
                                         constants.PANDAS_MONTH,
                                         constants.PANDAS_SEMESTER)

        prev_length = len(transform_col)
        handle_missing_values(self.col, transform_col)
        self.assertEqual(len(transform_col), prev_length - 2)

    def test_handle_month_quarter(self):
        transform_col = self.init_series("2000-05-01",
                                         constants.PANDAS_MONTH,
                                         constants.PANDAS_QUARTER)

        prev_length = len(transform_col)
        handle_missing_values(self.col, transform_col)
        self.assertEqual(len(transform_col), prev_length - 2)

    def test_handle_day_year(self):
        transform_col = self.init_series("2000-06-05",
                                         constants.PANDAS_DAY,
                                         constants.PANDAS_YEAR)

        prev_length = len(transform_col)
        handle_missing_values(self.col, transform_col)
        self.assertEqual(len(transform_col), prev_length - 2)

    def test_handle_day_month(self):
        transform_col = self.init_series("2000-06-05",
                                         constants.PANDAS_DAY,
                                         constants.PANDAS_MONTH)

        prev_length = len(transform_col)
        handle_missing_values(self.col, transform_col)
        self.assertEqual(len(transform_col), prev_length - 2)

    def test_handle_day_semester(self):
        transform_col = self.init_series("2000-06-05",
                                         constants.PANDAS_DAY,
                                         constants.PANDAS_SEMESTER)

        prev_length = len(transform_col)
        handle_missing_values(self.col, transform_col)
        self.assertEqual(len(transform_col), prev_length - 2)

    def test_handle_day_quarter(self):
        transform_col = self.init_series("2000-06-05",
                                         constants.PANDAS_DAY,
                                         constants.PANDAS_QUARTER)

        prev_length = len(transform_col)
        handle_missing_values(self.col, transform_col)
        self.assertEqual(len(transform_col), prev_length - 2)

    @raises(ValueError)
    def test_handle_missing_value_invalid_param(self):
        handle_incomplete_value(self.col, which='invalid')
