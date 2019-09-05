import os
from datetime import datetime
import pandas as pd

from django.test import TestCase

from series_tiempo_ar_api.libs.indexing import constants
from series_tiempo_ar_api.libs.indexing.constants import PANDAS_DAY, PANDAS_MONTH, PANDAS_WEEK, PANDAS_QUARTER, \
    PANDAS_SEMESTER, PANDAS_YEAR
from series_tiempo_ar_api.libs.indexing.indexer.operations import index_transform

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class DailyPeriodicityDistributionIndexingTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.short_dist = {
            'data': os.path.join(SAMPLES_DIR, 'daily_periodicity.csv'),
            'freq': constants.DAILY_FREQ,
            'year_ago_offset': {
                'daily': 365,
                'week': 53,
                'month': 12,
                'quarter': 4,
                'semester': 2,
                'year': 1,
            },
            'columns': ["tasas_interes_call", "tasas_interes_badlar", "tasas_interes_pm"],
            'index': 'dist1',
            'empty_intervals': ['quarter', 'semester', 'year']
        }
        cls.large_dist = {
            'data': os.path.join(SAMPLES_DIR, 'large_daily_periodicity.csv'),
            'freq': constants.DAILY_FREQ,
            'year_ago_offset': {
                'daily': 365,
                'week': 53,
                'month': 12,
                'quarter': 4,
                'semester': 2,
                'year': 1,
            },
            'columns': ["tasas_interes_call", "tasas_interes_badlar", "tasas_interes_pm"],
            'index': 'dist',
            'empty_intervals': []
        }

        cls.short_dist_data = _get_dist_data(cls.short_dist)
        cls.large_dist_data = _get_dist_data(cls.large_dist)

    # short dist tests

    def test_short_dist_quarter_semester_year_are_empty(self):
        for empty_interval_key in self.short_dist['empty_intervals']:
            self.assertEqual(len(self.short_dist_data[empty_interval_key].values), 0)

    def test_short_dist_daily_has_value_column(self):
        self._assert_key_only_included_in(self.short_dist_data["daily"],
                                          constants.VALUE,
                                          0)

    def test_short_dist_week_has_value_column(self):
        self._assert_key_only_included_in(self.short_dist_data["week"],
                                          constants.VALUE,
                                          0)

    def test_short_dist_month_has_value_column(self):
        self._assert_key_only_included_in(self.short_dist_data["month"],
                                          constants.VALUE,
                                          0)

    def test_short_dist_daily_has_change_column(self):
        self._assert_key_only_included_in(self.short_dist_data["daily"],
                                          constants.CHANGE,
                                          1)

    def test_short_dist_week_has_change_column(self):
        self._assert_key_only_included_in(self.short_dist_data["week"],
                                          constants.CHANGE,
                                          1)

    def test_short_dist_month_has_change_column(self):
        self._assert_key_only_included_in(self.short_dist_data["month"],
                                          constants.CHANGE,
                                          1)

    def test_short_dist_daily_has_pct_change_column(self):
        self._assert_key_only_included_in(self.short_dist_data["daily"],
                                          constants.PCT_CHANGE,
                                          1)

    def test_short_dist_week_has_pct_change_column(self):
        self._assert_key_only_included_in(self.short_dist_data["week"],
                                          constants.PCT_CHANGE,
                                          1)

    def test_short_dist_month_has_pct_change_column(self):
        self._assert_key_only_included_in(self.short_dist_data["month"],
                                          constants.PCT_CHANGE,
                                          1)

    def test_short_dist_daily_has_change_year_ago_column(self):
        self._assert_key_only_included_in(self.short_dist_data["daily"],
                                          constants.CHANGE_YEAR_AGO,
                                          self.short_dist['year_ago_offset']["daily"])

    def test_short_dist_week_has_change_year_ago_column(self):
        self._assert_key_only_included_in(self.short_dist_data["week"],
                                          constants.CHANGE_YEAR_AGO,
                                          self.short_dist['year_ago_offset']["week"])

    def test_short_dist_month_has_change_year_ago_column(self):
        self._assert_key_only_included_in(self.short_dist_data["month"],
                                          constants.CHANGE_YEAR_AGO,
                                          self.short_dist['year_ago_offset']["month"])

    def test_short_dist_daily_has_pct_change_year_ago_column(self):
        self._assert_key_only_included_in(self.short_dist_data["daily"],
                                          constants.PCT_CHANGE_YEAR_AGO,
                                          self.short_dist['year_ago_offset']["daily"])

    def test_short_dist_week_has_pct_change_year_ago_column(self):
        self._assert_key_only_included_in(self.short_dist_data["week"],
                                          constants.PCT_CHANGE_YEAR_AGO,
                                          self.short_dist['year_ago_offset']["week"])

    def test_short_dist_month_has_pct_change_year_ago_column(self):
        self._assert_key_only_included_in(self.short_dist_data["month"],
                                          constants.PCT_CHANGE_YEAR_AGO,
                                          self.short_dist['year_ago_offset']["month"])

    def test_short_dist_daily_has_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.short_dist_data["daily"],
                                          constants.CHANGE_BEG_YEAR,
                                          0)

    def test_short_dist_week_has_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.short_dist_data["week"],
                                          constants.CHANGE_BEG_YEAR,
                                          0)

    def test_short_dist_month_has_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.short_dist_data["month"],
                                          constants.CHANGE_BEG_YEAR,
                                          0)

    def test_short_dist_daily_has_pct_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.short_dist_data["daily"],
                                          constants.PCT_CHANGE_BEG_YEAR,
                                          0)

    def test_short_dist_week_has_pct_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.short_dist_data["week"],
                                          constants.PCT_CHANGE_BEG_YEAR,
                                          0)

    def test_short_dist_month_has_pct_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.short_dist_data["month"],
                                          constants.PCT_CHANGE_BEG_YEAR,
                                          0)

    def test_short_dist_daily_has_correct_change_value(self):
        self._assert_value_is_correct(self.short_dist_data["daily"],
                                      constants.CHANGE,
                                      1,
                                      1,
                                      lambda x, y: x - y)

    def test_short_dist_week_has_correct_change_value(self):
        self._assert_value_is_correct(self.short_dist_data["week"],
                                      constants.CHANGE,
                                      1,
                                      1,
                                      lambda x, y: x - y)

    def test_short_dist_month_has_correct_change_value(self):
        self._assert_value_is_correct(self.short_dist_data["month"],
                                      constants.CHANGE,
                                      1,
                                      1,
                                      lambda x, y: x - y)

    def test_short_dist_daily_has_correct_pct_change_value(self):
        self._assert_value_is_correct(self.short_dist_data["daily"],
                                      constants.PCT_CHANGE,
                                      1,
                                      1,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_short_dist_week_has_correct_pct_change_value(self):
        self._assert_value_is_correct(self.short_dist_data["week"],
                                      constants.PCT_CHANGE,
                                      1,
                                      1,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_short_dist_month_has_correct_pct_change_value(self):
        self._assert_value_is_correct(self.short_dist_data["month"],
                                      constants.PCT_CHANGE,
                                      1,
                                      1,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_short_dist_daily_has_correct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.short_dist_data["daily"],
                                      constants.CHANGE_YEAR_AGO,
                                      self.short_dist['year_ago_offset']["daily"],
                                      self.short_dist['year_ago_offset']["daily"],
                                      lambda x, y: x - y)

    def test_short_dist_week_has_correct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.short_dist_data["week"],
                                      constants.CHANGE_YEAR_AGO,
                                      self.short_dist['year_ago_offset']["week"],
                                      self.short_dist['year_ago_offset']["week"],
                                      lambda x, y: x - y)

    def test_short_dist_month_has_correct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.short_dist_data["month"],
                                      constants.CHANGE_YEAR_AGO,
                                      self.short_dist['year_ago_offset']["month"],
                                      self.short_dist['year_ago_offset']["month"],
                                      lambda x, y: x - y)

    def test_short_dist_daily_has_correct_pct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.short_dist_data["daily"],
                                      constants.PCT_CHANGE_YEAR_AGO,
                                      self.short_dist['year_ago_offset']["daily"],
                                      self.short_dist['year_ago_offset']["daily"],
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_short_dist_week_has_correct_pct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.short_dist_data["week"],
                                      constants.PCT_CHANGE_YEAR_AGO,
                                      self.short_dist['year_ago_offset']["week"],
                                      self.short_dist['year_ago_offset']["week"],
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_short_dist_month_has_correct_pct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.short_dist_data["month"],
                                      constants.PCT_CHANGE_YEAR_AGO,
                                      self.short_dist['year_ago_offset']["month"],
                                      self.short_dist['year_ago_offset']["month"],
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_short_dist_daily_has_correct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.short_dist_data["daily"],
                                                  constants.CHANGE_BEG_YEAR,
                                                  lambda x, y: x - y)

    def test_short_dist_week_has_correct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.short_dist_data["week"],
                                                  constants.CHANGE_BEG_YEAR,
                                                  lambda x, y: x - y)

    def test_short_dist_month_has_correct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.short_dist_data["month"],
                                                  constants.CHANGE_BEG_YEAR,
                                                  lambda x, y: x - y)

    def test_short_dist_daily_has_correct_pct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.short_dist_data["daily"],
                                                  constants.PCT_CHANGE_BEG_YEAR,
                                                  lambda x, y: (x - y) / y if y != 0 else 0)

    def test_short_dist_week_has_correct_pct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.short_dist_data["week"],
                                                  constants.PCT_CHANGE_BEG_YEAR,
                                                  lambda x, y: (x - y) / y if y != 0 else 0)

    def test_short_dist_month_has_correct_pct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.short_dist_data["month"],
                                                  constants.PCT_CHANGE_BEG_YEAR,
                                                  lambda x, y: (x - y) / y if y != 0 else 0)

    # long dist tests

    def test_large_dist_quarter_semester_year_are_empty(self):
        for empty_interval_key in self.large_dist['empty_intervals']:
            self.assertEqual(len(self.large_dist_data[empty_interval_key].values), 0)

    def test_large_dist_daily_has_value_column(self):
        self._assert_key_only_included_in(self.large_dist_data["daily"],
                                          constants.VALUE,
                                          0)

    def test_large_dist_week_has_value_column(self):
        self._assert_key_only_included_in(self.large_dist_data["week"],
                                          constants.VALUE,
                                          0)

    def test_large_dist_month_has_value_column(self):
        self._assert_key_only_included_in(self.large_dist_data["month"],
                                          constants.VALUE,
                                          0)

    def test_large_dist_quarter_has_value_column(self):
        self._assert_key_only_included_in(self.large_dist_data["quarter"],
                                          constants.VALUE,
                                          0)

    def test_large_dist_semester_has_value_column(self):
        self._assert_key_only_included_in(self.large_dist_data["semester"],
                                          constants.VALUE,
                                          0)

    def test_large_dist_year_has_value_column(self):
        self._assert_key_only_included_in(self.large_dist_data["year"],
                                          constants.VALUE,
                                          0)

    def test_large_dist_daily_has_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["daily"],
                                          constants.CHANGE,
                                          1)

    def test_large_dist_week_has_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["week"],
                                          constants.CHANGE,
                                          1)

    def test_large_dist_month_has_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["month"],
                                          constants.CHANGE,
                                          1)

    def test_large_dist_quarter_has_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["quarter"],
                                          constants.CHANGE,
                                          1)

    def test_large_dist_semester_has_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["semester"],
                                          constants.CHANGE,
                                          1)

    def test_large_dist_year_has_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["year"],
                                          constants.CHANGE,
                                          1)

    def test_large_dist_daily_has_pct_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["daily"],
                                          constants.PCT_CHANGE,
                                          1)

    def test_large_dist_week_has_pct_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["week"],
                                          constants.PCT_CHANGE,
                                          1)

    def test_large_dist_month_has_pct_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["month"],
                                          constants.PCT_CHANGE,
                                          1)

    def test_large_dist_quarter_has_pct_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["quarter"],
                                          constants.PCT_CHANGE,
                                          1)

    def test_large_dist_semester_has_pct_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["semester"],
                                          constants.PCT_CHANGE,
                                          1)

    def test_large_dist_year_has_pct_change_column(self):
        self._assert_key_only_included_in(self.large_dist_data["year"],
                                          constants.PCT_CHANGE,
                                          1)

    def test_large_dist_daily_has_change_year_ago_column(self):
        self._assert_key_only_included_in(self.large_dist_data["daily"],
                                          constants.CHANGE_YEAR_AGO,
                                          self.large_dist['year_ago_offset']["daily"])

    def test_large_dist_month_has_change_year_ago_column(self):
        self._assert_key_only_included_in(self.large_dist_data["month"],
                                          constants.CHANGE_YEAR_AGO,
                                          self.large_dist['year_ago_offset']["month"])

    def test_large_dist_quarter_has_change_year_ago_column(self):
        self._assert_key_only_included_in(self.large_dist_data["quarter"],
                                          constants.CHANGE_YEAR_AGO,
                                          self.large_dist['year_ago_offset']["quarter"])

    def test_large_dist_semester_has_change_year_ago_column(self):
        self._assert_key_only_included_in(self.large_dist_data["semester"],
                                          constants.CHANGE_YEAR_AGO,
                                          self.large_dist['year_ago_offset']["semester"])

    def test_large_dist_year_has_change_year_ago_column(self):
        self._assert_key_only_included_in(self.large_dist_data["year"],
                                          constants.CHANGE_YEAR_AGO,
                                          self.large_dist['year_ago_offset']["year"])

    def test_large_dist_daily_has_pct_change_year_ago_column(self):
        self._assert_key_only_included_in(self.large_dist_data["daily"],
                                          constants.PCT_CHANGE_YEAR_AGO,
                                          self.large_dist['year_ago_offset']["daily"])

    def test_large_dist_month_has_pct_change_year_ago_column(self):
        self._assert_key_only_included_in(self.large_dist_data["month"],
                                          constants.PCT_CHANGE_YEAR_AGO,
                                          self.large_dist['year_ago_offset']["month"])

    def test_large_dist_quarter_has_pct_change_year_ago_column(self):
        self._assert_key_only_included_in(self.large_dist_data["quarter"],
                                          constants.PCT_CHANGE_YEAR_AGO,
                                          self.large_dist['year_ago_offset']["quarter"])

    def test_large_dist_semester_has_pct_change_year_ago_column(self):
        self._assert_key_only_included_in(self.large_dist_data["semester"],
                                          constants.PCT_CHANGE_YEAR_AGO,
                                          self.large_dist['year_ago_offset']["semester"])

    def test_large_dist_year_has_pct_change_year_ago_column(self):
        self._assert_key_only_included_in(self.large_dist_data["year"],
                                          constants.PCT_CHANGE_YEAR_AGO,
                                          self.large_dist['year_ago_offset']["year"])

    def test_large_dist_daily_has_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.large_dist_data["daily"],
                                          constants.CHANGE_BEG_YEAR,
                                          0)

    def test_large_dist_month_has_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.large_dist_data["month"],
                                          constants.CHANGE_BEG_YEAR,
                                          0)

    def test_large_dist_quarter_has_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.large_dist_data["quarter"],
                                          constants.CHANGE_BEG_YEAR,
                                          0)

    def test_large_dist_semester_has_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.large_dist_data["semester"],
                                          constants.CHANGE_BEG_YEAR,
                                          0)

    def test_large_dist_year_has_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.large_dist_data["year"],
                                          constants.CHANGE_BEG_YEAR,
                                          0)

    def test_large_dist_daily_has_pct_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.large_dist_data["daily"],
                                          constants.PCT_CHANGE_BEG_YEAR,
                                          0)

    def test_large_dist_month_has_pct_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.large_dist_data["month"],
                                          constants.PCT_CHANGE_BEG_YEAR,
                                          0)

    def test_large_dist_quarter_has_pct_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.large_dist_data["quarter"],
                                          constants.PCT_CHANGE_BEG_YEAR,
                                          0)

    def test_large_dist_semester_has_pct_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.large_dist_data["semester"],
                                          constants.PCT_CHANGE_BEG_YEAR,
                                          0)

    def test_large_dist_year_has_pct_change_beg_of_year_column(self):
        self._assert_key_only_included_in(self.large_dist_data["year"],
                                          constants.PCT_CHANGE_BEG_YEAR,
                                          0)

    def test_large_dist_daily_has_correct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["daily"],
                                      constants.CHANGE,
                                      1,
                                      1,
                                      lambda x, y: x - y)

    def test_large_dist_week_has_correct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["week"],
                                      constants.CHANGE,
                                      1,
                                      1,
                                      lambda x, y: x - y)

    def test_large_dist_month_has_correct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["month"],
                                      constants.CHANGE,
                                      1,
                                      1,
                                      lambda x, y: x - y)

    def test_large_dist_quarter_has_correct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["quarter"],
                                      constants.CHANGE,
                                      1,
                                      1,
                                      lambda x, y: x - y)

    def test_large_dist_semester_has_correct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["semester"],
                                      constants.CHANGE,
                                      1,
                                      1,
                                      lambda x, y: x - y)

    def test_large_dist_year_has_correct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["year"],
                                      constants.CHANGE,
                                      1,
                                      1,
                                      lambda x, y: x - y)

    def test_large_dist_daily_has_correct_pct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["daily"],
                                      constants.PCT_CHANGE,
                                      1,
                                      1,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_week_has_correct_pct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["week"],
                                      constants.PCT_CHANGE,
                                      1,
                                      1,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_month_has_correct_pct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["month"],
                                      constants.PCT_CHANGE,
                                      1,
                                      1,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_quarter_has_correct_pct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["quarter"],
                                      constants.PCT_CHANGE,
                                      1,
                                      1,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_semester_has_correct_pct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["semester"],
                                      constants.PCT_CHANGE,
                                      1,
                                      1,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_year_has_correct_pct_change_value(self):
        self._assert_value_is_correct(self.large_dist_data["year"],
                                      constants.PCT_CHANGE,
                                      1,
                                      1,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_daily_has_correct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.large_dist_data["daily"],
                                      constants.CHANGE_YEAR_AGO,
                                      self.large_dist['year_ago_offset']["daily"],
                                      self.large_dist['year_ago_offset']["daily"],
                                      lambda x, y: x - y)

    def test_large_dist_month_has_correct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.large_dist_data["month"],
                                      constants.CHANGE_YEAR_AGO,
                                      self.large_dist['year_ago_offset']["month"],
                                      self.large_dist['year_ago_offset']["month"],
                                      lambda x, y: x - y)

    def test_large_dist_quarter_has_correct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.large_dist_data["quarter"],
                                      constants.CHANGE_YEAR_AGO,
                                      self.large_dist['year_ago_offset']["quarter"],
                                      self.large_dist['year_ago_offset']["quarter"],
                                      lambda x, y: x - y)

    def test_large_dist_semester_has_correct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.large_dist_data["semester"],
                                      constants.CHANGE_YEAR_AGO,
                                      self.large_dist['year_ago_offset']["semester"],
                                      self.large_dist['year_ago_offset']["semester"],
                                      lambda x, y: x - y)

    def test_large_dist_year_has_correct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.large_dist_data["year"],
                                      constants.CHANGE_YEAR_AGO,
                                      self.large_dist['year_ago_offset']["year"],
                                      self.large_dist['year_ago_offset']["year"],
                                      lambda x, y: x - y)

    def test_large_dist_daily_has_correct_pct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.large_dist_data["daily"],
                                      constants.PCT_CHANGE_YEAR_AGO,
                                      self.large_dist['year_ago_offset']["daily"],
                                      self.large_dist['year_ago_offset']["daily"],
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_month_has_correct_pct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.large_dist_data["month"],
                                      constants.PCT_CHANGE_YEAR_AGO,
                                      self.large_dist['year_ago_offset']["month"],
                                      self.large_dist['year_ago_offset']["month"],
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_quarter_has_correct_pct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.large_dist_data["quarter"],
                                      constants.PCT_CHANGE_YEAR_AGO,
                                      self.large_dist['year_ago_offset']["quarter"],
                                      self.large_dist['year_ago_offset']["quarter"],
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_semester_has_correct_pct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.large_dist_data["semester"],
                                      constants.PCT_CHANGE_YEAR_AGO,
                                      self.large_dist['year_ago_offset']["semester"],
                                      self.large_dist['year_ago_offset']["semester"],
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_year_has_correct_pct_change_a_year_ago_value(self):
        self._assert_value_is_correct(self.large_dist_data["year"],
                                      constants.PCT_CHANGE_YEAR_AGO,
                                      self.large_dist['year_ago_offset']["year"],
                                      self.large_dist['year_ago_offset']["year"],
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_daily_has_correct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.large_dist_data["daily"],
                                                  constants.CHANGE_BEG_YEAR,
                                                  lambda x, y: x - y)

    def test_large_dist_month_has_correct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.large_dist_data["month"],
                                                  constants.CHANGE_BEG_YEAR,
                                                  lambda x, y: x - y)

    def test_large_dist_quarter_has_correct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.large_dist_data["quarter"],
                                                  constants.CHANGE_BEG_YEAR,
                                                  lambda x, y: x - y)

    def test_large_dist_semester_has_correct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.large_dist_data["semester"],
                                                  constants.CHANGE_BEG_YEAR,
                                                  lambda x, y: x - y)

    def test_large_dist_year_has_correct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.large_dist_data["year"],
                                                  constants.CHANGE_BEG_YEAR,
                                                  lambda x, y: x - y)

    def test_large_dist_daily_has_correct_pct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.large_dist_data["daily"],
                                                  constants.PCT_CHANGE_BEG_YEAR,
                                                  lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_month_has_correct_pct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.large_dist_data["month"],
                                                  constants.PCT_CHANGE_BEG_YEAR,
                                                  lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_quarter_has_correct_pct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.large_dist_data["quarter"],
                                                  constants.PCT_CHANGE_BEG_YEAR,
                                                  lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_semester_has_correct_pct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.large_dist_data["semester"],
                                                  constants.PCT_CHANGE_BEG_YEAR,
                                                  lambda x, y: (x - y) / y if y != 0 else 0)

    def test_large_dist_year_has_correct_pct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(self.large_dist_data["year"],
                                                  constants.PCT_CHANGE_BEG_YEAR,
                                                  lambda x, y: (x - y) / y if y != 0 else 0)

    def _assert_key_only_included_in(self, _col, _key, _from):
        for row_index in range(0, min(_from, len(_col))):
            self.assertNotIn(_key, _col[row_index]["_source"])
        for row_index in range(_from, len(_col)):
            self.assertIn(_key, _col[row_index]["_source"])

    def _assert_value_is_correct(self, col, _key, _from, _offset, _function):
        for row_index in range(_from, len(col)):
            relative_index = row_index - _offset
            actual_values = col[row_index]["_source"]
            actual_value = actual_values[constants.VALUE]
            relative_value = col[relative_index]["_source"][constants.VALUE]
            expected_value = _function(actual_value, relative_value)
            self.assertAlmostEqual(expected_value, actual_values[_key])

    def _assert_year_ago_value_is_correct(self, data, _dict_keys, _key, _from, _offset, _function):
        for dict_key in _dict_keys:
            col = data[dict_key]
            for row_index in range(_from[dict_key], len(col)):
                relative_index = row_index - _offset[dict_key]
                actual_values = col[row_index]["_source"]
                actual_value = actual_values[constants.VALUE]
                relative_value = col[relative_index]["_source"][constants.VALUE]
                expected_value = _function(actual_value, relative_value)
                self.assertAlmostEqual(expected_value, actual_values[_key])

    def _assert_beg_of_year_value_is_correct(self, col, _key, _function):
        has_beg_value = False
        beg_of_year_value = 0
        for row in col:
            actual_values = row["_source"]
            actual_date = datetime.strptime(actual_values["timestamp"], '%Y-%m-%d').date()
            actual_value = actual_values[constants.VALUE]
            if actual_date.month == 1 and actual_date.day == 1:
                has_beg_value = True
                beg_of_year_value = actual_value
            expected_value = _function(actual_value, beg_of_year_value) if has_beg_value else 0
            self.assertAlmostEqual(expected_value, actual_values[_key])


def _get_dist_data(dist):
    df = _get_data_frame(dist["data"], dist['freq'], dist['columns'])
    col = df[df.columns[0]]
    series_id = col.name
    index = dist['index']
    data = dict()
    data["daily"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_DAY, 'avg')
    data["week"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_WEEK, 'avg')
    data["month"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_MONTH, 'avg')
    data["quarter"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_QUARTER, 'avg')
    data["semester"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_SEMESTER, 'avg')
    data["year"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_YEAR, 'avg')
    return data


def _get_data_frame(distribution_data, freq, columns):
    df = _read_catalog_csv(distribution_data)
    data = df.values
    new_index = pd.date_range(df.index[0], df.index[-1], freq=freq)

    # Chequeo de series de días hábiles (business days)
    if freq == constants.DAILY_FREQ and new_index.size > df.index.size:
        new_index = pd.date_range(df.index[0],
                                  df.index[-1],
                                  freq=constants.BUSINESS_DAILY_FREQ)
    return pd.DataFrame(index=new_index, data=data, columns=columns)


def _read_catalog_csv(distribution_data):
    return pd.read_csv(distribution_data, index_col="indice_tiempo")