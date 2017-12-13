#! coding: utf-8
from random import random
from datetime import datetime

from elasticsearch.helpers import parallel_bulk
from dateutil.relativedelta import relativedelta
from django.conf import settings

from series_tiempo_ar_api.apps.api.indexing.constants import INDEX_CREATION_BODY, FORCE_MERGE_SEGMENTS
from series_tiempo_ar_api.apps.api.query.constants import COLLAPSE_INTERVALS
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance
from series_tiempo_ar_api.apps.api.common import constants


class TestDataGenerator(object):
    date_format = '%Y-%m-%d'
    start_date = datetime(1910, 1, 1)
    max_data = settings.MAX_ALLOWED_VALUES['limit']

    def __init__(self):
        self.prev_values = []
        self.elastic = ElasticInstance()
        self.bulk_items = []

    def run(self):
        # Chequeo si existe el índice, si no, lo creo
        if not self.elastic.indices.exists(settings.TEST_INDEX):
            self.elastic.indices.create(settings.TEST_INDEX,
                                        body=INDEX_CREATION_BODY)

        for interval in COLLAPSE_INTERVALS:
            self.init_series(interval)

        for success, info in parallel_bulk(self.elastic, self.bulk_items):
            if not success:
                print("ERROR:", info)

        segments = FORCE_MERGE_SEGMENTS
        self.elastic.indices.forcemerge(index=settings.TEST_INDEX,
                                        max_num_segments=segments)

    def init_series(self, interval):
        """Crea varias series con periodicidad del intervalo dado"""

        start_date = self.start_date
        name = settings.TEST_SERIES_NAME.format(interval)
        self.generate_random_series(interval, name, self.start_date)
        start_date += relativedelta(years=50)
        delayed_name = settings.TEST_SERIES_NAME_DELAYED.format(interval)
        self.generate_random_series(interval, delayed_name, start_date)

    def generate_random_series(self, interval, series_name, start_date):
        self.prev_values = []

        current_date = start_date

        for _ in range(self.max_data):
            date_str = current_date.strftime(self.date_format)

            index_data = {
                "_index": settings.TEST_INDEX,
                "_id": series_name + '-' + date_str + '-' + interval + '-' + 'avg',
                "_type": settings.TS_DOC_TYPE,
                "_source": self.generate_properties(date_str, series_name, interval)
            }

            self.bulk_items.append(index_data)
            current_date = self.add_interval(current_date, interval)

    @staticmethod
    def add_interval(date, interval):

        if interval == 'day':
            return date + relativedelta(days=1)

        months_to_add = 0
        if interval == 'year':
            months_to_add = 12
        elif interval == 'semester':
            months_to_add = 6
        elif interval == 'quarter':
            months_to_add = 3
        elif interval == 'month':
            months_to_add = 1
        return date + relativedelta(months=months_to_add)

    def generate_properties(self, date_str, series_name, interval):
        """ Genera los valores del indicador aleatoriamente, junto con los
        valores de cambio y porcentuales"""
        properties = {
            'timestamp': date_str,
            constants.VALUE: 100000 + random() * 10000,
            constants.CHANGE: 1,
            constants.PCT_CHANGE: 1,
            constants.CHANGE_YEAR_AGO: 1,
            constants.PCT_CHANGE_YEAR_AGO: 1,
            'series_id': series_name,
            'interval': interval,
            'aggregation': 'avg'
        }

        if len(self.prev_values):
            # Calculos relacionados al valor anterior
            change = properties[constants.VALUE] - self.prev_values[-1][constants.VALUE]
            properties[constants.CHANGE] = change
            pct_change = properties[constants.VALUE] / self.prev_values[-1][constants.VALUE] - 1
            properties[constants.PCT_CHANGE] = pct_change

            date = datetime.strptime(date_str, self.date_format)
            for prev_value in self.prev_values:
                prev_date = datetime.strptime(prev_value['timestamp'],
                                              self.date_format)

                if date - relativedelta(years=1) == prev_date:
                    # Cálculos relacionados al valor del año pasado
                    change = properties[constants.VALUE] - prev_value[constants.VALUE]
                    properties[constants.CHANGE_YEAR_AGO] = change

                    pct_change = properties[constants.VALUE] / prev_value[constants.VALUE] - 1
                    properties[constants.PCT_CHANGE_YEAR_AGO] = pct_change
                    break

        self.prev_values.append(properties)
        # Los últimos 12 valores son, en el caso mensual, los del último año.
        # Me quedo sólo con esos valores como optimización
        self.prev_values = self.prev_values[-12:]
        return properties


def get_generator():
    return TestDataGenerator()
