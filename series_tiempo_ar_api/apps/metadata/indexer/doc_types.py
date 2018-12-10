#!coding=utf8
from elasticsearch_dsl import DocType, Keyword, Text, Date, MetaField

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class Metadata(DocType):
    """ Formato de los docs de metadatos a indexar en ES."""
    title = Keyword()
    description = Text(analyzer=constants.ANALYZER, copy_to='all')
    id = Keyword()
    dataset_title = Text(analyzer=constants.ANALYZER, copy_to='all')
    dataset_description = Text(analyzer=constants.ANALYZER, copy_to='all')
    dataset_theme = Keyword(copy_to='all')
    units = Keyword(copy_to='all')
    dataset_publisher_name = Keyword(copy_to='all')
    catalog_id = Keyword(copy_to='all')

    # Guardamos una copia como keyword para poder usar en aggregations
    dataset_source = Text(analyzer=constants.ANALYZER, copy_to='all')
    dataset_source_keyword = Keyword()

    periodicity = Keyword()
    start_date = Date()
    end_date = Date()

    all = Text(analyzer=constants.ANALYZER)

    class Meta:
        dynamic = MetaField('strict')
        doc_type = constants.METADATA_DOC_TYPE
        using = ElasticInstance.get()
