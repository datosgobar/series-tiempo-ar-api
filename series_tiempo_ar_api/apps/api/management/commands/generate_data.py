#! coding: utf-8
from random import random
from datetime import datetime

from elasticsearch.helpers import parallel_bulk
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.api.indexing import constants
from series_tiempo_ar_api.apps.api.query.constants import COLLAPSE_INTERVALS
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance


class Command(BaseCommand):
    date_format = '%Y-%m-%d'
    start_date = datetime(1910, 1, 1)
    max_data = settings.MAX_ALLOWED_VALUES['limit']
    series_per_interval = 2

    def __init__(self):
        BaseCommand.__init__(self)
        self.prev_values = []
        self.ES_URL = settings.ES_CONFIGURATION["ES_URLS"][0]
        self.elastic = ElasticInstance()
        self.bulk_items = []

    def handle(self, *args, **options):
        # Chequeo si existe el índice, si no, lo creo
        if not self.elastic.indices.exists(settings.TEST_INDEX):
            self.elastic.indices.create(settings.TEST_INDEX,
                                        body=constants.INDEX_CREATION_BODY)

        for interval in COLLAPSE_INTERVALS:
            for series_count in range(self.series_per_interval):
                self.generate_random_series(interval, series_count)

        for success, info in parallel_bulk(self.elastic, self.bulk_items):
            if not success:
                print("ERROR:", info)

    def generate_random_series(self, interval, series_count):
        self.prev_values = []

        current_date = self.start_date
        series_name = "random_series-{}-{}".format(interval, series_count)

        for _ in range(self.max_data):
            date_str = current_date.strftime(self.date_format)

            index_data = {
                "_index": settings.TEST_INDEX,
                "_id": series_name + '-' + date_str,
                "_type": settings.TS_DOC_TYPE,
                "_source": self.generate_properties(date_str, series_name)
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

    def generate_properties(self, date_str, series_name):
        """ Genera los valores del indicador aleatoriamente, junto con los
        valores de cambio y porcentuales"""
        properties = {
            'timestamp': date_str,
            'value': 100000 + random() * 10000,
            'change': 1,
            'percent_change': 1,
            'change_a_year_ago': 1,
            'percent_change_a_year_ago': 1,
            'series_id': series_name
        }

        if len(self.prev_values):
            # Calculos relacionados al valor anterior
            change = properties['value'] - self.prev_values[-1]['value']
            properties['change'] = change
            pct_change = properties['value'] / self.prev_values[-1]['value'] - 1
            properties['percent_change'] = pct_change

            date = datetime.strptime(date_str, self.date_format)
            for prev_value in self.prev_values:
                prev_date = datetime.strptime(prev_value['timestamp'],
                                              self.date_format)

                if date - relativedelta(years=1) == prev_date:
                    # Cálculos relacionados al valor del año pasado
                    change = properties['value'] - prev_value['value']
                    properties['change_a_year_ago'] = change

                    pct_change = properties['value'] / prev_value['value'] - 1
                    properties['percent_change_a_year_ago'] = pct_change
                    break

        self.prev_values.append(properties)
        # Los últimos 12 valores son, en el caso mensual, los del último año.
        # Me quedo sólo con esos valores como optimización
        self.prev_values = self.prev_values[-12:]
        return properties
