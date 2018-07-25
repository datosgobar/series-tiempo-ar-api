#! coding: utf-8
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.analytics.tasks import import_analytics_from_api_mgmt


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--all', default=False, action='store_true')

    def handle(self, *args, **options):
        import_all = options['all']
        import_analytics_from_api_mgmt(import_all=import_all)
