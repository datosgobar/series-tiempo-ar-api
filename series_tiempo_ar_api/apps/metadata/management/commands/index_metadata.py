#! coding: utf-8

from django.core.management import BaseCommand
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer import run_metadata_indexer


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('datajson_url', nargs='*')

    def handle(self, *args, **options):
        task = IndexMetadataTask()
        task.save()
        run_metadata_indexer.delay(task)
        self.stdout.write("Indexación inicializada")
