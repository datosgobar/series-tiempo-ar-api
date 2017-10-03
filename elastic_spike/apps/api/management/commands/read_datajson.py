#! coding: utf-8
import requests
from django.core.management import BaseCommand, CommandError
from requests.exceptions import RequestException

from elastic_spike.apps.api.query.catalog_reader import ReaderPipeline


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('catalog')
        parser.add_argument('--index', action='store_true')

    def handle(self, *args, **options):
        catalog_url = options['catalog']

        index_only = options.get('index')
        try:
            response = requests.head(catalog_url)
        except RequestException:
            raise CommandError("URL inválida")

        if response.status_code != 200:
            error = u"Catálogo no leído. Status code: {}"
            raise CommandError(error.format(response.status_code))

        ReaderPipeline(catalog_url, index_only)
