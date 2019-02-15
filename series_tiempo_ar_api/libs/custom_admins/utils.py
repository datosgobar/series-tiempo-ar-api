from elasticsearch_dsl import Search, Q
from series_tiempo_ar_api.apps.metadata import constants


def delete_metadata(fields: list):
    search = Search(index=constants.METADATA_ALIAS)
    return search.filter('terms', id=[field.identifier for field in fields]).delete()
