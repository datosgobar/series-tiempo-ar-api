#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import A

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Metadata


def query_field_terms(field=None, search=None):
    """Devuelve todos los 'field' únicos cargados en los metadatos de Field,
    usando un Terms aggregation en el índice de Elasticsearch
    """
    if search is None:
        search = Metadata.search(index=constants.METADATA_ALIAS)

    search = setup_field_terms_search(field, search)
    search_result = search.execute()

    return format_response(search_result)


def format_response(search_result):
    sources = [source['key']
               for source in search_result.aggregations.results.buckets]
    response = {
        'data': sources
    }
    return response


def setup_field_terms_search(field, search):
    if not field:
        raise ValueError(u'Field a buscar inválido')

    agg = A('terms', field=field, size=settings.MAX_DATASET_SOURCES)
    search.aggs.bucket('results', agg)
    search = search[:0]  # Descarta resultados de search, solo nos importa el aggregation
    return search
