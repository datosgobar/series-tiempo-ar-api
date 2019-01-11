from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.management.tasks.integration_test import run_integration_test


class Command(BaseCommand):

    def handle(self, *args, **options):
        run_integration_test()
