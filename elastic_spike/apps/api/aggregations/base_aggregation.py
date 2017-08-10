#! coding: utf-8

from elasticsearch import Elasticsearch


class BaseAggregation:
    date_format = '%Y-%m-%dT%H:%M:%S.000Z'

    def __init__(self):
        self.result = {'errors': []}
        self.elastic = Elasticsearch()

    def execute(self, series, request_args):
        raise NotImplementedError
