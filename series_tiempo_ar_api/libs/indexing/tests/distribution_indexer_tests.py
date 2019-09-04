import os
from datetime import datetime
from unittest import mock
import pandas as pd

from django.test import TestCase
from django_datajsonar.models import Distribution, Catalog, Node, ReadDataJsonTask
from django_datajsonar.tasks import read_datajson

from series_tiempo_ar_api.libs.indexing import constants
from series_tiempo_ar_api.libs.indexing.constants import PANDAS_DAY, PANDAS_MONTH, PANDAS_WEEK, PANDAS_QUARTER, \
    PANDAS_SEMESTER, PANDAS_YEAR
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer
from series_tiempo_ar_api.libs.indexing.indexer.operations import process_column, index_transform

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class DistributionIndexerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Catalog.objects.all().delete()

    def test_index_series_no_identifier(self):
        catalog = os.path.join(SAMPLES_DIR, 'series_metadata_no_identifier.json')
        self._index_catalog(catalog)

        distribution = Distribution.objects.first()

        actions = DistributionIndexer('some_index').generate_es_actions(distribution)

        self.assertFalse(actions)

    def _index_catalog(self, catalog_path):
        self.read_data(catalog_path)
        with mock.patch('series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer.parallel_bulk'):
            distributions = Distribution.objects.all()

            for distribution in distributions:
                DistributionIndexer('some_index').reindex(distribution)

    def read_data(self, catalog_path):
        Node.objects.create(catalog_id='test_catalog', catalog_url=catalog_path, indexable=True)
        task = ReadDataJsonTask.objects.create()

        read_datajson(task, whitelist=True)


class DailyPeriodicityDistributionIndexingTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        distribution_data = os.path.join(SAMPLES_DIR, 'daily_periodicity.csv')
        dist_freq = constants.DAILY_FREQ
        cls.year_ago_offset = 365
        columns = ["tasas_interes_call", "tasas_interes_badlar", "tasas_interes_pm"]
        df = _get_data_frame(distribution_data, dist_freq, columns)
        col = df[df.columns[0]]
        index = "some_index"
        series_id = col.name
        cls.data = dict()
        cls.data["daily"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_DAY, 'avg')
        cls.data["week"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_WEEK, 'avg')
        cls.data["month"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_MONTH, 'avg')
        cls.data["quarter"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_QUARTER, 'avg')
        cls.data["semester"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_SEMESTER, 'avg')
        cls.data["year"] = index_transform(col, lambda x: x.mean(), index, series_id, PANDAS_YEAR, 'avg')

    def test_daily_week_month_has_value_column(self):
        self._assert_key_in_dict(["daily", "week", "month"], constants.VALUE, 0)

    def test_daily_week_month_has_change_column(self):
        self._assert_key_in_dict(["daily", "week", "month"], constants.CHANGE, 1)

    def test_daily_week_month_has_pct_change_column(self):
        self._assert_key_in_dict(["daily", "week", "month"], constants.PCT_CHANGE, 1)

    def test_daily_week_month_has_change_a_year_ago_column(self):
        self._assert_key_in_dict(["daily", "week", "month"], constants.CHANGE_YEAR_AGO, self.year_ago_offset)

    def test_daily_week_month_has_pct_change_a_year_ago_column(self):
        self._assert_key_in_dict(["daily", "week", "month"], constants.PCT_CHANGE_YEAR_AGO, self.year_ago_offset)

    def test_daily_week_month_has_change_beg_of_year_column(self):
        self._assert_key_in_dict(["daily", "week", "month"], constants.CHANGE_BEG_YEAR, 0)

    def test_daily_week_month_has_pct_change_beg_of_year_column(self):
        self._assert_key_in_dict(["daily", "week", "month"], constants.PCT_CHANGE_BEG_YEAR, 0)

    def test_quarter_semester_year_are_empty(self):
        self.assertEqual(len(self.data["semester"].values), 0)
        self.assertEqual(len(self.data["quarter"].values), 0)
        self.assertEqual(len(self.data["year"].values), 0)

    def test_daily_week_month_has_correct_change_value(self):
        self._assert_value_is_correct(["daily", "week", "month"],
                                      constants.CHANGE, 1, 1, lambda x, y: x - y)

    def test_daily_week_month_has_correct_pct_change_value(self):
        self._assert_value_is_correct(["daily", "week", "month"],
                                      constants.PCT_CHANGE, 1, 1,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_daily_week_month_has_correct_change_a_year_ago_value(self):
        self._assert_value_is_correct(["daily", "week", "month"],
                                      constants.CHANGE_YEAR_AGO,
                                      self.year_ago_offset,
                                      self.year_ago_offset,
                                      lambda x, y: x - y)

    def test_daily_week_month_has_correct_pct_change_a_year_ago_value(self):
        self._assert_value_is_correct(["daily", "week", "month"],
                                      constants.PCT_CHANGE_YEAR_AGO,
                                      self.year_ago_offset,
                                      self.year_ago_offset,
                                      lambda x, y: (x - y) / y if y != 0 else 0)

    def test_daily_week_month_has_correct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(["daily", "week", "month"],
                                                  constants.CHANGE_BEG_YEAR,
                                                  lambda x, y: x - y)

    def test_daily_week_month_has_correct_pct_change_beg_of_year_value(self):
        self._assert_beg_of_year_value_is_correct(["daily", "week", "month"],
                                                  constants.PCT_CHANGE_BEG_YEAR,
                                                  lambda x, y: (x - y) / y if y != 0 else 0)

    def _assert_key_in_dict(self, _dict_keys, _key, _from):
        for dict_key in _dict_keys:
            col = self.data[dict_key]
            for row_index in range(0, min(_from, len(col))):
                self.assertNotIn(_key, col[row_index]["_source"])
            for row_index in range(_from, len(col)):
                self.assertIn(_key, col[row_index]["_source"])

    def _assert_value_is_correct(self, _dict_keys, _key, _from, _offset, _function):
        for dict_key in _dict_keys:
            col = self.data[dict_key]
            for row_index in range(_from, len(col)):
                relative_index = row_index - _offset
                actual_values = col[row_index]["_source"]
                actual_value = actual_values[constants.VALUE]
                relative_value = col[relative_index]["_source"][constants.VALUE]
                expected_value = _function(actual_value, relative_value)
                self.assertAlmostEqual(expected_value, actual_values[_key])

    def _assert_beg_of_year_value_is_correct(self, _dict_keys, _key, _function):
        for dict_key in _dict_keys:
            col = self.data[dict_key]
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