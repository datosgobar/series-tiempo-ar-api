from io import BytesIO

import pandas as pd
from django.core.management import BaseCommand
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
        IntegrationTest(series_metadata=series_metadata, api_url='http://localhost:8999/').test()
