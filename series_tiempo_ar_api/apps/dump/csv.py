#!coding=utf8
import os
import csv
import json
import zipfile

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django_datajsonar.models import Field, Node
from pydatajson import DataJson
from elasticsearch.helpers import scan

from series_tiempo_ar_api.apps.dump.models import DumpFile
from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.api.helpers import periodicity_human_format_to_iso
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from . import constants


class CSVDumpGenerator:
    def __init__(self,
                 task,
                 index=settings.TS_INDEX,
                 output_directory=constants.DUMP_DIR):
        self.task = task
        self.index = index
        self.output_directory = output_directory
        self.fields = {}
        self.catalog_themes = {}
        self.elastic = ElasticInstance.get()
        self.init_fields_dict()

    def init_fields_dict(self):
        """Inicializa en un diccionario con IDs de series como clave los valores a escribir en cada
        uno de los CSV.
        """
        fields = Field.objects.filter(
            enhanced_meta__key=meta_keys.AVAILABLE,
        ).prefetch_related(
            'distribution',
            'distribution__dataset',
            'distribution__dataset__catalog',
            'enhanced_meta',
        )

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
                'dataset_tema': self.get_theme(field.distribution.dataset.catalog.identifier, dataset_meta),
                'dataset_responsable': dataset_meta.get('publisher', {}).get('name'),
                'dataset_titulo': field.distribution.dataset.title,
                'dataset_fuente': dataset_meta.get('source'),
            }

    def generate(self):
        os.makedirs(self.output_directory, exist_ok=True)

        self.generate_csv(constants.FULL_CSV,
                          constants.FULL_CSV_HEADER,
                          self.full_csv_row)
        self.generate_csv(constants.VALUES_CSV,
                          constants.VALUES_HEADER,
                          self.values_csv_row)
        self.zip_full_csv()

        for filename in constants.FILES + [constants.FULL_CSV]:
            self.remove_old_dumps(filename)

    def values_csv_row(self, field, source):
        return [
            self.fields[field]['catalog_id'],
            self.fields[field]['dataset_id'],
            self.fields[field]['distribution_id'],
            field,
            source.get('timestamp'),
            source.get('value'),
            periodicity_human_format_to_iso(source.get('interval')),
        ]

    def full_csv_row(self, field, source):
        return [
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

    def generate_csv(self, filename, header, row_gen):
        """Escribe el dump al filepath especificado, con el header row especificado,
        sacando los datos a partir del callable 'row_gen', llamado una vez por valor
        guardado en la base de datos
        """
        path = os.path.join(self.output_directory, filename)
        with default_storage.open(path, 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(header)

            query = {'query': {'match': {'raw_value': True}}}
            for res in scan(self.elastic, index=self.index, query=query):
                source = res['_source']

                field = source['series_id']
                if field not in self.fields:
                    continue
                row = row_gen(field, source)
                writer.writerow(row)

            self.task.dumpfile_set.create(file_name=filename, file=File(f))

    def zip_full_csv(self):
        zip_path = os.path.join(self.output_directory, constants.FULL_CSV_ZIPPED)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_name:
            filepath = self.task.dumpfile_set.get(file_name=constants.FULL_CSV).file.path
            zip_name.write(filepath, arcname=constants.FULL_CSV)

        self.task.dumpfile_set.create(file_name=constants.FULL_CSV_ZIPPED,
                                      file=File(default_storage.open(zip_path, 'rb')))

    def get_or_init_catalog_themes(self, catalog_id):
        """Devuelve un dict ID: label de los themes del catálogo"""
        if catalog_id in self.catalog_themes:
            return self.catalog_themes[catalog_id]

        # No lo tenemos guardado, parseo el datajson
        catalog = DataJson(json.loads(Node.objects.get(catalog_id=catalog_id).catalog))

        self.catalog_themes[catalog_id] = {}
        for theme in catalog.get_themes():
            self.catalog_themes[catalog_id][theme['id']] = theme['label']

        return self.catalog_themes[catalog_id]

    def get_theme(self, catalog_id, dataset_meta):
        """Devuelve un string con los themes del dataset separados por comas"""
        labels = []
        for theme in dataset_meta.get('theme', []):
            labels.append(self.get_or_init_catalog_themes(catalog_id)[theme])

        return ','.join(labels)

    def remove_old_dumps(self, dump_file_name):
        same_file = DumpFile.objects.filter(file_name=dump_file_name)
        old = same_file.order_by('-id')[constants.OLD_DUMP_FILES_AMOUNT:]
        for dump_file in old:
            try:
                os.remove(dump_file.file.path)
            except FileNotFoundError:
                pass

        same_file.filter(id__in=old.values_list('id', flat=True)).delete()
