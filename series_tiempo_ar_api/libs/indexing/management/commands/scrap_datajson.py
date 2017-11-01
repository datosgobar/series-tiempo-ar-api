#! coding: utf-8
import requests
from django.core.management import BaseCommand
from series_tiempo_ar_api.libs.indexing.tasks import scrap


from series_tiempo_ar_api.apps.api.query.catalog_reader import ReaderPipeline, Scraper


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('catalog')
        parser.add_argument('--async', action='store_true')

    def handle(self, *args, **options):
        catalog_url = options['catalog']
        run_async = options.get('async')

        if run_async:
            scrap.delay(catalog_url)
        else:
            scrap(catalog_url)

