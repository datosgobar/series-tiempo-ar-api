#! coding: utf-8
import logging

from django_rq import job
from elasticsearch import Elasticsearch

from elasticsearch_dsl.connections import connections
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.apps.metadata.indexer.units import update_units
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from series_tiempo_ar_api.apps.metadata.utils import get_random_index_name
from .catalog_meta_indexer import CatalogMetadataIndexer

logger = logging.getLogger(__name__)


class MetadataIndexer:

    def __init__(self, task):
        self.elastic: Elasticsearch = connections.get_connection()
        self.task = task

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
        index = get_random_index_name()
        index_created = False
        for node in Node.objects.filter(indexable=True):
            try:
                IndexMetadataTask.info(self.task,
                                       u'Inicio de la indexación de metadatos de {}'
                                       .format(node.catalog_id))
                index_created = CatalogMetadataIndexer(node, self.task, index).index() or index_created
                IndexMetadataTask.info(self.task, u'Fin de la indexación de metadatos de {}'
                                       .format(node.catalog_id))
            except Exception as e:
                IndexMetadataTask.info(self.task,
                                       u'Error en la lectura del catálogo {}: {}'.format(node.catalog_id, e))

        if index_created:
            self.elastic.indices.forcemerge(index=index)
            self.update_alias(index)
        else:
            if self.elastic.indices.exists(index):
                self.elastic.indices.delete(index)


@job('meta_indexing', timeout=10000)
def run_metadata_indexer(task):
    MetadataIndexer(task).run()
    update_units()
    task.refresh_from_db()
    task.status = task.FINISHED
    task.save()


@job('meta_indexing', timeout=-1)
def enqueue_new_index_metadata_task():
    run_metadata_indexer(IndexMetadataTask.objects.create())
