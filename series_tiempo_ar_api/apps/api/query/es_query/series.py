#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import Search, Q, A

from series_tiempo_ar_api.apps.api.helpers import extra_offset
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class Series(object):
    def __init__(self, index, series_id, rep_mode, args, collapse_agg=None):
        self.index = index
        self.elastic = ElasticInstance.get()
        self.series_id = series_id
        self.rep_mode = rep_mode
        self.args = args.copy()
        self.collapse_agg = collapse_agg or constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]
        self.search = self.init_search()

    def init_search(self):
        search = Search(using=self.elastic, index=self.index)
        end = self.args[constants.PARAM_START] + self.args[constants.PARAM_LIMIT]
        search = search[self.args[constants.PARAM_START]:end]
        search = search.sort(settings.TS_TIME_INDEX_FIELD)  # Default: ascending sort
        # Filtra los resultados por la serie pedida. Si se hace en memoria filtramos
        # por la agg default, y calculamos la agg pedida en runtime
        agg = self.collapse_agg if self.collapse_agg not in constants.IN_MEMORY_AGGS else constants.AGG_DEFAULT
        search = search.filter('bool',
                               must=[Q('match', series_id=self.series_id),
                                     Q('match', aggregation=agg)])

        return search

    def add_range_filter(self, start, end):
        _filter = {
            'lte': end,
            'gte': start
        }
        self.search = self.search.filter('range', timestamp=_filter)

    def add_collapse(self, periodicity):
        if self.collapse_agg not in constants.IN_MEMORY_AGGS:
            self.search = self.search.filter('bool', must=[Q('match', interval=periodicity)])

        elif periodicity != self.args[constants.PARAM_PERIODICITY]:
            # Agregamos la aggregation (?) para que se ejecute en ES en runtime
            self.search = self.search.filter('bool', must=[Q('match', interval=self.args['periodicity'])])
            self.search.aggs.bucket('test',
                                    A('date_histogram',
                                      field='timestamp',
                                      interval=periodicity,
                                      format='yyyy-MM-dd').
                                    metric('test', self.collapse_agg, field=self.rep_mode))
        else:  # Ignoramos la in memory ag
            self.collapse_agg = constants.AGG_DEFAULT
            self.search = self.search.filter('bool', must=[Q('match', interval=periodicity)])

        self.args[constants.PARAM_PERIODICITY] = periodicity

    def add_pagination(self, start, limit):
        # ☢️☢️☢️
        es_offset = start + limit
        if self.rep_mode != constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE]:
            es_offset += extra_offset(self.args[constants.PARAM_PERIODICITY])

        self.search = self.search[start:es_offset]
