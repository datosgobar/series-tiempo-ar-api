#! coding: utf-8
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.analytics.tasks import import_last_day_analytics


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_last_day_analytics()
