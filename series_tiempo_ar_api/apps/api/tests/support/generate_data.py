#! coding: utf-8
from random import random
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from elasticsearch.helpers import parallel_bulk
from django.conf import settings

from series_tiempo_ar_api.apps.api.helpers import interval_to_freq_pandas
from series_tiempo_ar_api.apps.api.indexing.constants import INDEX_CREATION_BODY, \
    FORCE_MERGE_SEGMENTS
from series_tiempo_ar_api.apps.api.query.constants import COLLAPSE_INTERVALS
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance
from series_tiempo_ar_api.apps.api.common import operations


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

        result = []
        for interval in COLLAPSE_INTERVALS:
            name = settings.TEST_SERIES_NAME.format(interval)
            result.extend(self.init_series(name, interval, self.start_date))
            delayed_name = settings.TEST_SERIES_NAME_DELAYED.format(interval)
            delayed_date = self.start_date + relativedelta(years=50)
            result.extend(self.init_series(delayed_name, interval, delayed_date))

        for success, info in parallel_bulk(self.elastic, result):
            if not success:
                print("ERROR:", info)

        segments = FORCE_MERGE_SEGMENTS
        self.elastic.indices.forcemerge(index=settings.TEST_INDEX,
                                        max_num_segments=segments)

    def init_series(self, name, interval, start_date):
        """Crea varias series con periodicidad del intervalo dado"""

        freq = interval_to_freq_pandas(interval)
        if interval == 'year' or interval == 'semester':
            index = pd.date_range(start=str(start_date), end="2260", freq=freq)
        else:
            index = pd.date_range(start=str(start_date), periods=self.max_data, freq=freq)

        col = pd.Series(index=index,
                        name=name,
                        data=[100000 + random() * 10000 for _ in range(len(index))])

        return operations.process_column(col, settings.TEST_INDEX)


def get_generator():
    return TestDataGenerator()
