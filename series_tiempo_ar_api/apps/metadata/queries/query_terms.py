#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import A

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Metadata


def query_field_terms(field=None):
    """Devuelve todos los 'field' únicos cargados en los metadatos de Field,
    usando un Terms aggregation en el índice de Elasticsearch
    """

    if not field:
        raise ValueError(u'Field a buscar inválido')

    search = Metadata.search(index=constants.METADATA_ALIAS)

    agg = A('terms', field=field, size=settings.MAX_DATASET_SOURCES)
    search.aggs.bucket('results', agg)

    search = search[:0]  # Descarta resultados de search, solo nos importa el aggregation
    search_result = search.execute()

    sources = [{"label": source['key'], "series_count": source['doc_count']}
               for source in search_result.aggregations.results.buckets]
    response = {
        'data': sources
    }
    return response
