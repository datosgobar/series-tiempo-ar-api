#! coding: utf-8
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.dump.tasks import enqueue_xlsx_dump_task


class Command(BaseCommand):
    def handle(self, *args, **options):
        enqueue_xlsx_dump_task()
