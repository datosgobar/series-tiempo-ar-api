#! coding: utf-8

from elasticsearch import Elasticsearch


class BaseAggregation:
    def __init__(self):
        self.result = {}
        self.elastic = Elasticsearch()

    def execute(self, request_args):
        raise NotImplementedError
