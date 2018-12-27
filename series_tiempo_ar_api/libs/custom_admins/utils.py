from elasticsearch_dsl import Search, Q
from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


def delete_metadata(fields: list):
    es_instance = ElasticInstance.get()

    search = Search(using=es_instance, index=constants.METADATA_ALIAS)
    return search.filter('terms', id=[field.identifier for field in fields]).delete()
