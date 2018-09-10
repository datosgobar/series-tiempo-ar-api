#! coding: utf-8
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.dump.tasks import enqueue_csv_dump_task


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--index', type=str, default=None)

    def handle(self, *args, **options):
        enqueue_csv_dump_task()
