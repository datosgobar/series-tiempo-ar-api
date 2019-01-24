#! coding: utf-8
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.analytics.tasks import enqueue_new_import_analytics_task


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--all', default=False, action='store_true')

    def handle(self, *args, **options):
        import_all = options['all']
        enqueue_new_import_analytics_task(import_all=import_all)
