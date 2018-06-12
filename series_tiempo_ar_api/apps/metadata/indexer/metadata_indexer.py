#! coding: utf-8
import logging
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import Node
from series_tiempo_ar_api.apps.metadata.indexer.catalog_metadata_indexer import \
    CatalogMetadataIndexer
from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance

logger = logging.getLogger(__name__)


class MetadataIndexer:

    def __init__(self, doc_type=Field):
        self.elastic = ElasticInstance.get()
        self.doc_type = doc_type

    def init_index(self):
        if self.elastic.indices.exists(self.doc_type.Meta.index):
            self.doc_type.init(using=self.elastic)

    def run(self):
        self.init_index()
        for node in Node.objects.filter(indexable=True):
            try:
                data_json = DataJson(node.catalog_url)
                CatalogMetadataIndexer(data_json, node.catalog_id).index()
            except Exception as e:
                logger.exception(u'Error en la lectura del catálogo: %s', e)
