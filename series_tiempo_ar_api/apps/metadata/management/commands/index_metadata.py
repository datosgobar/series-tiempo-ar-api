#! coding: utf-8

import logging
from django.core.management import BaseCommand
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import Node
from series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer import MetadataIndexer


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('datajson_url', nargs='*')

    def handle(self, *args, **options):
        if options['datajson_url']:
            urls = options['datajson_url']
        else:
            urls = [node.catalog_url for node in Node.objects.filter(indexable=True)]

        for url in urls:
            try:
                data_json = DataJson(url)
                MetadataIndexer(data_json).index()
            except Exception as e:
                logger.exception(u'Error en la lectura del catálogo: %s', e)
