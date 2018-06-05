#!coding=utf8
import json

from django_datajsonar.models import Metadata, Node, ReadDataJsonTask, \
    Field, Distribution
from django_datajsonar.tasks import read_datajson
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer


def get_available_fields():
    available_ids = Metadata.objects.filter(
        key=meta_keys.AVAILABLE,
        content_type__model='field'
    ).values_list('object_id')
    return Field.objects.filter(id__in=available_ids).exclude(title='indice_tiempo')


def index_catalog(catalog_id, catalog_path, index, node=None):
    """Indexa un catálogo. Útil para tests"""
    if not node:
        node = Node(catalog_id=catalog_id,
                    catalog_url=catalog_path,
                    indexable=True)

    catalog = DataJson(node.catalog_url)
    node.catalog = json.dumps(catalog)
    node.save()
    task = ReadDataJsonTask()
    task.save()

    read_datajson(task, read_local=True, whitelist=True)
    for distribution in Distribution.objects.filter(dataset__catalog__identifier=catalog_id):
        DistributionIndexer(index=index).run(distribution)
    ElasticInstance.get().indices.forcemerge(index=index)
