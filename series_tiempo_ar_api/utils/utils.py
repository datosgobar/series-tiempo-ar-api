#!coding=utf8
import csv
import codecs
import json

from django_datajsonar.models import Metadata, Node, ReadDataJsonTask, \
    Field, Distribution
from django_datajsonar.tasks import read_datajson
from elasticsearch_dsl.connections import connections
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer
from series_tiempo_ar_api.libs.indexing.popularity import update_popularity_metadata


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

        for field in distribution.field_set.all():
            for key in meta_keys.HITS_KEYS:
                field.enhanced_meta.create(key=key, value=0)

    connections.get_connection().indices.forcemerge(index=index)


def read_file_as_csv(file):
    reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
    return reader
