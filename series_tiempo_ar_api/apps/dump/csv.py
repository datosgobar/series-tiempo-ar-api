#!coding=utf8
import os
import csv

from django.conf import settings
from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.api.helpers import periodicity_human_format_to_iso
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from elasticsearch.helpers import scan

from . import constants


class CSVDumpGenerator:
    def __init__(self):
        self.fields = {}
        self.elastic = ElasticInstance.get()
        self.init_fields_dict()

    def init_fields_dict(self):
        fields = Field.objects.all().prefetch_related('distribution',
                                                      'distribution__dataset',
                                                      'distribution__dataset__catalog')

        for field in fields:
            self.fields[field.identifier] = {
                'catalog_id': field.distribution.dataset.catalog.identifier,
                'dataset_id': field.distribution.dataset.identifier,
                'distribution_id': field.distribution.identifier,
            }

    def generate(self):
        self.generate_values_csv()

    def generate_values_csv(self):
        filepath = os.path.join(settings.MEDIA_ROOT, constants.VALUES_CSV)

        with open(filepath, 'w') as f:
            writer = csv.writer(f)
            writer.writerow([  # Header
                'catalogo_id',
                'dataset_id',
                'distribucion_id',
                'serie_id',
                'indice_tiempo',
                'valor',
                'indice_tiempo_frecuencia'])

            query = {'query': {'match': {'raw_value': True}}}  # solo valores crudos
            for res in scan(self.elastic, index='indicators', query=query):
                source = res['_source']

                field = source['series_id']
                if field not in self.fields:
                    continue
                row = [
                    self.fields[field]['catalog_id'],
                    self.fields[field]['dataset_id'],
                    self.fields[field]['distribution_id'],
                    field,
                    source.get('timestamp'),
                    source.get('value'),
                    periodicity_human_format_to_iso(source.get('interval')),
                ]
                writer.writerow(row)
