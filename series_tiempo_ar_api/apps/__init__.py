from django.conf import settings

from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance

es_configurations = settings.ES_CONFIGURATION
urls = es_configurations["ES_URLS"]
client_options = es_configurations["CONNECTIONS"]["default"]
ElasticInstance.init(urls, client_options)
