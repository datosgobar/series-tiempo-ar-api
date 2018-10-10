#! coding: utf-8
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask
from series_tiempo_ar_api.apps.dump.tasks import enqueue_dump_task


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--index', type=str, default=None)

    def handle(self, *args, **options):
        task = GenerateDumpTask.objects.create(file_type=GenerateDumpTask.TYPE_CSV)
        enqueue_dump_task(task)
