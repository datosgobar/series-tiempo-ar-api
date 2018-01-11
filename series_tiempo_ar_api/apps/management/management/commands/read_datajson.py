#! coding: utf-8
import logging

from django.core.management import BaseCommand
from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.indexing import catalog_reader
from series_tiempo_ar_api.apps.management.models import Node

logger = logging.getLogger(__name__)

READ_ERROR = u"Error en la lectura del catálogo %s: %s"


class Command(BaseCommand):
    def handle(self, *args, **options):
        nodes = Node.objects.filter(indexable=True)
        for node in nodes:
            catalog_id = node.catalog_id
            catalog_url = node.catalog_url
            try:
                catalog = DataJson(catalog_url)
            except (IOError, ValueError, AssertionError) as e:
                self.stderr.write(READ_ERROR % (catalog_id, e))
                logging.warn(READ_ERROR, catalog_id, e)
                continue

            catalog_reader.index_catalog(catalog, catalog_id)
