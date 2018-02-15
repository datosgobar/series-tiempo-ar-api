#! coding: utf-8

import logging
from django.core.management import BaseCommand
from pydatajson import DataJson

from series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer import MetadataIndexer


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('datajson_url')

    def handle(self, *args, **options):
        try:
            data_json = DataJson(options['datajson_url'])
            MetadataIndexer(data_json).index()
        except Exception as e:
            logger.exception(u'Error en la lectura del catálogo: %s', e)
