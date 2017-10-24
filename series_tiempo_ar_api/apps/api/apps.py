from django.apps import AppConfig
from django.conf import settings

from .query.elastic import ElasticInstance


class ApiConfig(AppConfig):
    name = 'series_tiempo_ar_api.apps.api'

    def ready(self):
        ES_URLS = settings.ES_CONFIGURATION["ES_URLS"]
        ElasticInstance.init(ES_URLS)
