#!coding=utf8
import os
import csv
import json
import zipfile

from django.conf import settings
from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.api.helpers import periodicity_human_format_to_iso
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from elasticsearch.helpers import scan

from . import constants


class CSVDumpGenerator:
    def __init__(self, index=settings.TS_INDEX, output_directory=None):
        if not output_directory:
            output_directory = os.path.join(settings.MEDIA_ROOT, 'dump')
        self.index = index
        self.output_directory = output_directory
        self.fields = {}
        self.elastic = ElasticInstance.get()
        self.init_fields_dict()

    def init_fields_dict(self):
        fields = Field.objects.all().prefetch_related('distribution',
                                                      'distribution__dataset',
                                                      'distribution__dataset__catalog')

        for field in fields:
            meta = json.loads(field.metadata)
            dist_meta = json.loads(field.distribution.metadata)
            dataset_meta = json.loads(field.distribution.dataset.metadata)
            self.fields[field.identifier] = {
                'catalog_id': field.distribution.dataset.catalog.identifier,
                'dataset_id': field.distribution.dataset.identifier,
                'distribution_id': field.distribution.identifier,
                'serie_titulo': field.title,
                'serie_unidades': meta.get('units'),
                'serie_descripcion': meta.get('description'),
                'distribucion_descripcion': dist_meta.get('description'),
                'dataset_tema': dataset_meta.get('theme'),
                'dataset_responsable': dataset_meta.get('publisher', {}).get('name'),
                'dataset_titulo': field.distribution.dataset.title,
                'dataset_fuente': dataset_meta.get('source'),
            }

    def generate(self):
        self.generate_values_csv()
        self.generate_full_csv()
        self.zip_full_csv()

    def generate_values_csv(self):
        filepath = os.path.join(self.output_directory, constants.VALUES_CSV)

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
            for res in scan(self.elastic, index=self.index, query=query):
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

    def generate_full_csv(self):
        filepath = os.path.join(self.output_directory, constants.FULL_CSV)
        with open(filepath, 'w') as f:
            writer = csv.writer(f)
            writer.writerow([  # Header
                'catalogo_id',
                'dataset_id',
                'distribucion_id',
                'serie_id',
                'indice_tiempo',
                'indice_tiempo_frecuencia',
                'valor',
                'serie_titulo',
                'serie_unidades',
                'serie_descripcion',
                'distribucion_descripcion',
                'dataset_tema',
                'dataset_responsable',
                'dataset_fuente',
                'dataset_titulo',
            ])
            query = {'query': {'match': {'raw_value': True}}}  # solo valores crudos
            for res in scan(self.elastic, index=self.index, query=query):
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
                    periodicity_human_format_to_iso(source.get('interval')),
                    source.get('value'),
                    self.fields[field]['serie_titulo'],
                    self.fields[field]['serie_unidades'],
                    self.fields[field]['serie_descripcion'],
                    self.fields[field]['distribucion_descripcion'],
                    self.fields[field]['dataset_tema'],
                    self.fields[field]['dataset_responsable'],
                    self.fields[field]['dataset_fuente'],
                    self.fields[field]['dataset_titulo'],
                ]
                writer.writerow(row)

    def zip_full_csv(self):
        zip_path = os.path.join(self.output_directory, constants.FULL_CSV_ZIPPED)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_name:
            filepath = os.path.join(self.output_directory, constants.FULL_CSV)
            zip_name.write(filepath, arcname=constants.FULL_CSV)
