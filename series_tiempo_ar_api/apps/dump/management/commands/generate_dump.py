#! coding: utf-8
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.dump import csv


class Command(BaseCommand):

    def handle(self, *args, **options):
        csv.generate_values_csv()

