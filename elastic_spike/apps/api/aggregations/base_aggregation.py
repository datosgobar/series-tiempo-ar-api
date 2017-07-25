#! coding: utf-8

from elasticsearch import Elasticsearch


class BaseAggregation:
    def __init__(self):
        self.result = {'errors': []}
        self.elastic = Elasticsearch()

    def execute(self, series, request_args):
        raise NotImplementedError
