#! coding: utf-8
import argparse
from datetime import date, datetime

from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.analytics.elasticsearch.indicators import calculate_hits_indicators


class Command(BaseCommand):
    help = "Calcula indicadores de consultas de todas las series, para el día especificado"

    def add_arguments(self, parser):
        parser.add_argument('date', type=valid_date,
                            help='Fecha para la cual calcular los indicadores')

    def handle(self, *args, **options):
        for_date = options['date']
        calculate_hits_indicators(for_date)
        self.stdout.write("Indexación de queries a ES comenzada")


# Robado descaradamente de stackoverflow
def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)
