#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import A

from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field


def query_field_terms(field=None):
    """Devuelve todos los 'field' únicos cargados en los metadatos de Field,
    usando un Terms aggregation en el índice de Elasticsearch
    """

    if not field:
        raise ValueError(u'Field a buscar inválido')

    search = Field.search()

    agg = A('terms', field=field, size=settings.MAX_DATASET_SOURCES)
    search.aggs.bucket('results', agg)

    search = search[:0]  # Descarta resultados de search, solo nos importa el aggregation
    search_result = search.execute()

    sources = [source['key'] for source in search_result.aggregations.results.buckets]
    response = {
        'data': sources
    }
    return response
