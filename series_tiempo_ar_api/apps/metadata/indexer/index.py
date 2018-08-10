#! coding: utf-8
from elasticsearch_dsl import Index, analyzer, token_filter

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


def add_analyzer(index: Index):
    """Agrega un nuevo analyzer al índice, disponible para ser usado
    en todos sus fields. El analyzer aplica lower case + ascii fold:
    quita acentos y uso de ñ, entre otros, para permitir búsqueda de
    texto en español
    """

    synonyms_filter = token_filter(constants.SYNONYM_FILTER,
                                   type='synonym',
                                   synonyms=['motos,example_synonym'])

    index.analyzer(
        analyzer(constants.ANALYZER,
                 tokenizer='standard',
                 filter=['lowercase', 'asciifolding', synonyms_filter])
    )


def get_fields_meta_index():
    fields_meta = Index(constants.FIELDS_INDEX, using=ElasticInstance.get())

    add_analyzer(fields_meta)
    return fields_meta
