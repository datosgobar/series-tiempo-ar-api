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


class MetadataIndexer:

    def __init__(self, task):
        self.elastic: Elasticsearch = connections.get_connection()
        self.task = task

    def update_alias(self, index_name, new_index=True):
        if not self.elastic.indices.exists_alias(name=constants.METADATA_ALIAS):
            self.elastic.indices.put_alias(index_name, constants.METADATA_ALIAS)
            return

        actions = [
            {"add": {"index": index_name, "alias": constants.METADATA_ALIAS}},
        ]

        if new_index:
            indices = self.elastic.indices.get_alias(name=constants.METADATA_ALIAS).keys()
            for old_index in indices:
                actions.append({"remove_index": {"index": old_index}})

        self.elastic.indices.update_aliases({
            "actions": actions
        })

    def run(self, nodes, single_node=False):
        new_index = \
            not single_node or \
            not self.elastic.indices.exists_alias(name=constants.METADATA_ALIAS)
        index = get_random_index_name() if new_index else constants.METADATA_ALIAS
        index_created = False
        for node in nodes:
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
            self.update_alias(index, new_index=new_index)
        elif self.elastic.indices.exists(index):
            self.elastic.indices.delete(index)


@job('meta_indexing', timeout=10000)
def run_metadata_indexer(task):
    single_node = bool(task.node)
    nodes = [task.node] if single_node else Node.objects.filter(indexable=True)
    MetadataIndexer(task).run(nodes, single_node=single_node)
    update_units()
    task.refresh_from_db()
    task.status = task.FINISHED
    task.save()


@job('meta_indexing', timeout=-1)
def enqueue_new_index_metadata_task(node=None):
    run_metadata_indexer(IndexMetadataTask.objects.create(node=node))
