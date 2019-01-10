import json
from io import BytesIO, StringIO

import pandas as pd
from django.core.management import BaseCommand
from django.urls import reverse
from django.test.client import Client

from scripts.integration_test import IntegrationTest
from series_tiempo_ar_api.apps.dump.models import DumpFile


class Command(BaseCommand):

    def handle(self, *args, **options):
        metadata = DumpFile.objects.filter(node=None,
                                           file_type=DumpFile.TYPE_CSV,
                                           file_name=DumpFile.FILENAME_METADATA).last()

        if not metadata:
            return

        series_metadata = pd.read_csv(BytesIO(metadata.file.read()), index_col='serie_id')
        IntegrationTest(series_metadata=series_metadata, fetcher=DjangoSeriesFetcher()).test()


class DjangoSeriesFetcher:

    def __init__(self):
        self.client = Client()

    def fetch(self, series_id, **kwargs):
        data = {'ids': series_id, 'format': 'csv'}
        data.update(kwargs)
        response = self.client.get(reverse('api:series:series'), data=data)

        if response.status_code != 200:
            return None

        csv = StringIO(str(response.content, encoding='utf8'))

        return pd.read_csv(csv, parse_dates=['indice_tiempo'], index_col='indice_tiempo')
