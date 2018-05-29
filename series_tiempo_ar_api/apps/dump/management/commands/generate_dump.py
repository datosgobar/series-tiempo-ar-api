#! coding: utf-8
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.dump.csv import CSVDumpGenerator


class Command(BaseCommand):

    def handle(self, *args, **options):
        csv_gen = CSVDumpGenerator()
        csv_gen.generate()
