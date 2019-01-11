from io import StringIO, BytesIO

import pandas as pd
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django_rq import job

from scripts.integration_test import IntegrationTest
from series_tiempo_ar_api.apps.dump.models import DumpFile


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


@job("default", timeout=-1)
def run_integration_test():
    metadata = DumpFile.objects.filter(node=None,
                                       file_type=DumpFile.TYPE_CSV,
                                       file_name=DumpFile.FILENAME_METADATA).last()

    if not metadata:
        return

    series_metadata = pd.read_csv(BytesIO(metadata.file.read()), index_col='serie_id')
    setattr(settings, "ALLOWED_HOSTS", ["*"])
    IntegrationTest(series_metadata=series_metadata, fetcher=DjangoSeriesFetcher()).test()
