# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from django.conf import settings

from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class MetadataConfig(AppConfig):
    name = 'series_tiempo_ar_api.apps.metadata'

    es_configurations = settings.ES_CONFIGURATION
    es_urls = es_configurations["ES_URLS"]
    client_options = es_configurations["CONNECTIONS"]["default"]
    ElasticInstance.init(es_urls, client_options)
