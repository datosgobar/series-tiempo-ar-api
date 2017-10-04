from django.apps import AppConfig
from django.conf import settings

from .query.elastic import ElasticInstance


class ApiConfig(AppConfig):
    name = 'elastic_spike.apps.api'

    def ready(self):
        ElasticInstance.init(settings.ES_URL)
