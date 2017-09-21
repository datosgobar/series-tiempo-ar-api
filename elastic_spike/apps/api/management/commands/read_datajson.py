#! coding: utf-8
import requests

from requests.exceptions import RequestException
from django.core.management import BaseCommand, CommandError

from elastic_spike.apps.api.catalog_reader import ReaderPipeline


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('catalog')

    def handle(self, *args, **options):
        catalog_url = options['catalog']

        try:
            response = requests.get(catalog_url)
        except RequestException:
            raise CommandError("URL inválida")

        if response.status_code != 200:
            error = "Catálogo no leído. Status code: {}"
            raise CommandError(error.format(response.status_code))

        if response.json():
            ReaderPipeline(response.json())
