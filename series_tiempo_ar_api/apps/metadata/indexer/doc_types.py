#!coding=utf8
from elasticsearch_dsl import DocType, Keyword, Text

from series_tiempo_ar_api.apps.metadata import constants


class Field(DocType):
    """ Formato de los docs de metadatos a indexar en ES."""
    title = Keyword()
    description = Text()
    id = Keyword()
    dataset_title = Text()
    dataset_description = Text()
    theme_description = Text()
    dataset_source = Text()

    class Meta:
        index = constants.FIELDS_INDEX
