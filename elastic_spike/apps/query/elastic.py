#! coding: utf-8
from elasticsearch import Elasticsearch


class ElasticInstance(object):

    elastic = Elasticsearch()

    @classmethod
    def get(cls):
        return cls.elastic
