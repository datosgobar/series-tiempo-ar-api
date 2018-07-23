#! coding: utf-8
import logging

from django_rq import job

from django_datajsonar.models import Node
from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from .enhanced_meta_indexer import CatalogMetadataIndexer

logger = logging.getLogger(__name__)


class MetadataIndexer:

    def __init__(self, task, doc_type=Field):
        self.task = task
        self.elastic = ElasticInstance.get()
        self.doc_type = doc_type
        self.index = self.doc_type._doc_type.index

    def init_index(self):
        if not self.elastic.indices.exists(self.index):
            self.doc_type.init(using=self.elastic)

        # Actualizo el mapping por si se agregan nuevos campos
        self.doc_type._doc_type.refresh()

    def run(self):
        self.init_index()
        for node in Node.objects.filter(indexable=True):
            try:
                IndexMetadataTask.info(self.task,
                                       u'Inicio de la indexación de metadatos de {}'
                                       .format(node.catalog_id))
                CatalogMetadataIndexer(node, self.task, self.doc_type).index()
                IndexMetadataTask.info(self.task, u'Fin de la indexación de metadatos de {}'
                                       .format(node.catalog_id))

            except Exception as e:
                IndexMetadataTask.info(self.task,
                                       u'Error en la lectura del catálogo {}: {}'.format(node.catalog_id, e))

        self.elastic.indices.forcemerge(self.index)


@job('indexing', timeout=10000)
def run_metadata_indexer(task):
    MetadataIndexer(task).run()
    task.refresh_from_db()
    task.status = task.FINISHED
    task.save()
