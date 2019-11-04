#! coding: utf-8
import json
import os
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from django.conf import settings
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl.connections import connections

from series_tiempo_ar_api.apps.api.helpers import interval_to_freq_pandas
from series_tiempo_ar_api.apps.api.query.constants import COLLAPSE_INTERVALS
from series_tiempo_ar_api.apps.api.tests.support.test_data_values import START_DATE, START_VALUE, END_DATE
from series_tiempo_ar_api.libs.indexing.constants import INDEX_CREATION_BODY, \
    FORCE_MERGE_SEGMENTS
from series_tiempo_ar_api.libs.indexing.indexer import operations

DATA_FILE_NAME = 'data.csv'
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), DATA_FILE_NAME)


class TestDataGenerator:
    date_format = '%Y-%m-%d'

    def __init__(self):
        self.prev_values = []
        self.elastic = connections.get_connection()
        self.bulk_items = []

    def run(self):
        try:
            self.index_data()
        except IOError:  # No hay data precargada, la generamos
            self.init_data()
            self.index_data()

    def index_data(self):
        """Indexa la data leía desde el archivo de datos"""
        with open(DATA_FILE_PATH) as f:
            self.elastic.indices.create(settings.TS_INDEX,
                                        body=INDEX_CREATION_BODY)

            actions = [json.loads(row) for row in f.readlines()]
            for success, info in parallel_bulk(self.elastic, actions):
                if not success:
                    print("ERROR:", info)

            segments = FORCE_MERGE_SEGMENTS
            self.elastic.indices.forcemerge(index=settings.TS_INDEX,
                                            max_num_segments=segments)

    def init_data(self):

        result = []
        for interval in COLLAPSE_INTERVALS:
            name = settings.TEST_SERIES_NAME.format(interval)
            result.extend(self.init_series(name, interval, START_DATE))
            delayed_name = settings.TEST_SERIES_NAME_DELAYED.format(interval)
            delayed_date = START_DATE + relativedelta(years=5)
            result.extend(self.init_series(delayed_name, interval, delayed_date))

        with open(DATA_FILE_PATH, 'w') as f:
            f.writelines([json.dumps(row) + '\n' for row in result])

    def init_series(self, name, interval, start_date):
        """Crea varias series con periodicidad del intervalo dado"""

        freq = interval_to_freq_pandas(interval)
        index = pd.date_range(start=str(start_date), end=str(END_DATE), freq=freq, closed='left')

        col = pd.Series(index=index,
                        name=name,
                        data=[START_VALUE + i for i in range(len(index))])

        return operations.process_column(col, settings.TS_INDEX)


def get_generator():
    return TestDataGenerator()
