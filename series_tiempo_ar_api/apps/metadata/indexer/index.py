#! coding: utf-8
from elasticsearch_dsl import Index, analyzer

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


def add_analyzer(index: Index):
    index.analyzer(
        analyzer(constants.ANALYZER,
                 tokenizer='standard',
                 filter=['lowercase', 'asciifolding'])
    )


fields_meta = Index(constants.FIELDS_INDEX, using=ElasticInstance.get())

add_analyzer(fields_meta)
