#! coding: utf-8
import requests
import yaml
from django.core.management import BaseCommand
from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.indexing.catalog_reader import index_catalog

CATALOGS_INDEX = 'https://raw.githubusercontent.com/datosgobar/libreria-catalogos/master/indice.yml'


class Command(BaseCommand):
    def handle(self, *args, **options):
        catalogs = yaml.load(requests.get(CATALOGS_INDEX).text)

        for catalog_id, values in catalogs.items():
            if values['federado'] and values['formato'] == 'json':
                try:
                    catalog = DataJson(values['url'])
                except (IOError, ValueError):
                    continue

                index_catalog(catalog, catalog_id)
