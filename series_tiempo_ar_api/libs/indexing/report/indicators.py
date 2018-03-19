#! coding: utf-8
from redis import Redis

from django.conf import settings
from series_tiempo_ar_api.apps.management.models import Indicator, Node


class IndicatorLoader(object):
    """Lee y escribe valores de indicadores al store de Redis"""

    def __init__(self):
        self.redis = Redis(host=settings.DEFAULT_REDIS_HOST,
                           port=settings.DEFAULT_REDIS_PORT,
                           db=int(settings.DEFAULT_REDIS_DB))

    def load_indicators_into_db(self, task):
        """Carga todas las variables de indicadores guardadas a la base de datos en modelos Indicator,
        asociados a la task pasada
        """
        for node in Node.objects.filter(indexable=True):
            for indicator, _ in Indicator.TYPE_CHOICES:
                value = self.redis.get(self.fmt(node.catalog_id, indicator))
                if value:
                    task.indicator_set.create(type=indicator, value=value, node=node)

    def increment_indicator(self, catalog_id, indicator, amt=1):
        self.redis.incr(self.fmt(catalog_id, indicator), amt)

    def clear_indicators(self):
        """Borra todas las variables guardadas relacionadas a indicadores del store"""
        for node in Node.objects.all():
            for indicator, _ in Indicator.TYPE_CHOICES:
                self.redis.delete(self.fmt(node.catalog_id, indicator))

    def fmt(self, catalog_id, indicator):
        """Devuelve un string que identifique al par catalogo-indicador para usar como key en redis"""
        return catalog_id + indicator

    def get(self, catalog_id, indicator):
        return self.redis.get(self.fmt(catalog_id, indicator))
