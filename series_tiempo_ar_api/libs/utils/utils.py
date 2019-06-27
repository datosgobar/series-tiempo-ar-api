#!coding=utf8
import csv
import codecs
import json

from elasticsearch_dsl.connections import connections
from pydatajson import DataJson
from django_datajsonar.models import Node, ReadDataJsonTask, \
    Distribution
from django_datajsonar.tasks import read_datajson

from series_tiempo_ar_api.apps.management import models as mgmt, meta_keys
from series_tiempo_ar_api.libs.indexing.tasks import index_distribution


def index_catalog(catalog_id, catalog_path, index, node=None):
    """Indexa un catálogo. Útil para tests"""
    node = parse_catalog(catalog_id, catalog_path, node)

    index_task = mgmt.IndexDataTask.objects.create()
    for distribution in Distribution.objects.filter(dataset__catalog__identifier=catalog_id):
        index_distribution(distribution.identifier, node.id, index_task.id, index=index, force=True)

        for field in distribution.field_set.all():
            for key in meta_keys.HITS_KEYS:
                field.enhanced_meta.create(key=key, value=0)

    es_client = connections.get_connection()
    if es_client.indices.exists(index=index):
        es_client.indices.forcemerge(index=index)


def parse_catalog(catalog_id, catalog_path, node=None):
    if not node:
        node = Node.objects.create(catalog_id=catalog_id,
                                   catalog_url=catalog_path,
                                   indexable=True)
    catalog = DataJson(node.catalog_url)
    node.catalog = json.dumps(catalog)
    node.save()
    task = ReadDataJsonTask()
    task.save()
    read_datajson(task, whitelist=True)
    return node


def read_file_as_csv(file):
    reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
    return reader
