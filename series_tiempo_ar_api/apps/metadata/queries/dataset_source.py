#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import A

from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field


def dataset_source_query():
    """Devuelve todos los dataset_source únicos cargados en los metadatos de Field"""

    search = Field.search()

    agg = A('terms', field='dataset_source_keyword', size=settings.MAX_DATASET_SOURCES)
    search.aggs.bucket('sources', agg)

    search = search[:0]  # Descarta resultados de search, solo nos importa el aggregation
    search_result = search.execute()

    sources = [source['key'] for source in search_result.aggregations.sources.buckets]
    response = {
        'sources': sources
    }
    return response
