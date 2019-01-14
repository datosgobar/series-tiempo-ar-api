from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.management.models import IntegrationTestTask
from series_tiempo_ar_api.apps.management.tasks.integration_test import run_integration


class Command(BaseCommand):

    def handle(self, *args, **options):
        task = IntegrationTestTask.objects.create()
        run_integration(task=task)
