#! coding: utf-8
import logging
import random

from django_rq import job
from django.utils import timezone
from elasticsearch import Elasticsearch

from elasticsearch_dsl import Index
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from .doc_types import Field
from .catalog_meta_indexer import CatalogMetadataIndexer
from .index import get_fields_meta_index

logger = logging.getLogger(__name__)


class MetadataIndexer:

    def __init__(self, task, doc_type=Field, index: Index = None):
        self.elastic: Elasticsearch = ElasticInstance.get()
        self.task = task
        self.index = index if index is not None else get_fields_meta_index()
        self.doc_type = doc_type

    def update_alias(self, index_name):
        if not self.elastic.indices.exists_alias(name=constants.METADATA_ALIAS):
            self.elastic.indices.put_alias(index_name, constants.METADATA_ALIAS)
            return
        indices = self.elastic.indices.get_alias(name=constants.METADATA_ALIAS).keys()

        actions = [
            {"add": {"index": index_name, "alias": constants.METADATA_ALIAS}},
        ]

        for old_index in indices:
            actions.append({"remove_index": {"index": old_index}})

        self.elastic.indices.update_aliases({
            "actions": actions
        })

    def run(self):
        index = f"metadata-{random.randrange(1000000)}-{int(timezone.now().timestamp())}"
        index_ok = False
        for node in Node.objects.filter(indexable=True):
            try:
                IndexMetadataTask.info(self.task,
                                       u'Inicio de la indexación de metadatos de {}'
                                       .format(node.catalog_id))
                CatalogMetadataIndexer(node, self.task, index).index()
                IndexMetadataTask.info(self.task, u'Fin de la indexación de metadatos de {}'
                                       .format(node.catalog_id))
            except Exception as e:
                IndexMetadataTask.info(self.task,
                                       u'Error en la lectura del catálogo {}: {}'.format(node.catalog_id, e))

        self.index.forcemerge()

        if index_ok:
            self.index.forcemerge()
            self.update_alias(index)


@job('indexing', timeout=10000)
def run_metadata_indexer(task):
    MetadataIndexer(task).run()
    task.refresh_from_db()
    task.status = task.FINISHED
    task.save()
