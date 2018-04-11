#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import Search, Q

from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class Series(object):
    def __init__(self, index, series_id, rep_mode, args, collapse_agg=None):
        self.index = index
        self.elastic = ElasticInstance.get()
        self.series_id = series_id
        self.rep_mode = rep_mode
        self.args = args
        self.collapse_agg = collapse_agg or constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]
        self.search = self.init_search()

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def get(self, item, default=None):
        return getattr(self, item, default)

    def init_search(self):
        search = Search(using=self.elastic, index=self.index)
        end = self.args[constants.PARAM_START] + self.args[constants.PARAM_LIMIT]
        search = search[self.args[constants.PARAM_START]:end]
        search = search.sort(settings.TS_TIME_INDEX_FIELD)  # Default: ascending sort
        # Filtra los resultados por la serie pedida
        search = search.filter('bool',
                               must=[Q('match', series_id=self.series_id),
                                     Q('match', aggregation=self.collapse_agg)])
        return search
