#! coding: utf-8
import requests
import yaml
from django.core.management import BaseCommand, CommandError
from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.indexing.catalog_reader import index_catalog

CATALOGS_INDEX = 'https://raw.githubusercontent.com/datosgobar/libreria-catalogos/master/indice.yml'
MISSING_ARG_MSG = u"URL y name deben ser especificados a la vez"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--url', dest='url', type=unicode, default=None)
        parser.add_argument('--name', dest='name', type=unicode, default=None)

    def handle(self, *args, **options):
        url = options['url']
        name = options['name']
        if url or name:
            if not name or not url:
                raise CommandError(MISSING_ARG_MSG)
            index_catalog(DataJson(url), name)
            return

        catalogs = yaml.load(requests.get(CATALOGS_INDEX).text)

        for catalog_id, values in catalogs.items():
            if values['federado'] and values['formato'] == 'json':
                try:
                    catalog = DataJson(values['url'])
                except (IOError, ValueError):
                    continue

                index_catalog(catalog, catalog_id)
