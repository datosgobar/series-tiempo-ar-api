#! coding: utf-8

from django.core.management import BaseCommand
from series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer import MetadataIndexer


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('datajson_url')

    def handle(self, *args, **options):
        MetadataIndexer().index(options['datajson_url'])
