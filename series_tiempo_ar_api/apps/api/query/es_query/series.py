#! coding: utf-8
from elasticsearch_dsl import Search


class Series(object):
    def __init__(self, series_id, rep_mode, search, collapse_agg=None):
        self.series_id = series_id
        self.rep_mode = rep_mode
        self.search = search or Search()
        self.collapse_agg = collapse_agg
        self.meta = None

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def get(self, item, default=None):
        return getattr(self, item, default)
