#! coding: utf-8
from elasticsearch_dsl import Index, analyzer, token_filter

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.apps.metadata.models import Synonym
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


def add_analyzer(index: Index):
    """Agrega un nuevo analyzer al índice, disponible para ser usado
    en todos sus fields. El analyzer aplica lower case + ascii fold:
    quita acentos y uso de ñ, entre otros, para permitir búsqueda de
    texto en español
    """

    synonyms = list(Synonym.objects.values_list('terms', flat=True))

    filters = ['lowercase', 'asciifolding']
    if synonyms:
        filters.append(token_filter(constants.SYNONYM_FILTER,
                                    type='synonym',
                                    synonyms=synonyms))

    index.analyzer(
        analyzer(constants.ANALYZER,
                 tokenizer='standard',
                 filter=filters)
    )


def get_fields_meta_index():
    fields_meta = Index(constants.METADATA_ALIAS, using=ElasticInstance.get())

    add_analyzer(fields_meta)
    return fields_meta
