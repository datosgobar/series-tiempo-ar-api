from django.apps import AppConfig
from django.conf import settings

from .query.elastic import ElasticInstance


class ApiConfig(AppConfig):
    name = 'series_tiempo_ar_api.apps.api'

    def ready(self):
        es_configurations = settings.ES_CONFIGURATION
        urls = es_configurations["ES_URLS"]
        client_options = es_configurations["CONNECTIONS"]["default"]
        ElasticInstance.init(urls, client_options)
