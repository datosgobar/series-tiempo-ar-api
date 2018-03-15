#! coding: utf-8
from redis import Redis

from series_tiempo_ar_api.apps.management.models import Indicator, Node


class IndicatorLoader(object):

    def __init__(self):
        self.redis = Redis()

    def load_indicators(self, task):
        for node in Node.objects.filter(indexable=True):
            for indicator, _ in Indicator.TYPE_CHOICES:
                value = self.redis.get(node.catalog_id + indicator)
                if value:
                    task.indicator_set.create(type=indicator, value=value, node=node)

    def increment_indicator(self, catalog_id, indicator, amt=1):
        self.redis.incr(catalog_id + indicator, amt)

    def clear_indicators(self):
        for node in Node.objects.all():
            for indicator, _ in Indicator.TYPE_CHOICES:
                self.redis.delete(node.catalog_id + indicator)
