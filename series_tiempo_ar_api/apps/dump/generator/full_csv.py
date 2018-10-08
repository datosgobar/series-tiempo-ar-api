import os
import zipfile

from django.core.files import File
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.apps.dump.models import DumpFile
from .abstract_dump_gen import AbstractDumpGenerator
from .dump_csv_writer import CsvDumpWriter


class FullCsvGenerator(AbstractDumpGenerator):
    filename = DumpFile.FILENAME_FULL

    def generate(self):
        filepath = self.get_file_path()
        CsvDumpWriter(self.task, self.fields, self.full_csv_row).write(filepath, constants.FULL_CSV_HEADER)

        self.write(filepath, DumpFile.FILENAME_FULL)
        self.zip_full_csv(filepath)

    @staticmethod
    def full_csv_row(value, fields, field, periodicity):
        dataset = fields[field]['dataset']
        return (
            dataset.catalog.identifier,
            dataset.identifier,
            fields[field]['distribution'].identifier,
            field,
            value[0].date(),  # Index
            periodicity,
            value[1],  # Value
            fields[field]['serie_titulo'],
            fields[field]['serie_unidades'],
            fields[field]['serie_descripcion'],
            fields[field]['distribucion_descripcion'],
            fields[field]['dataset_tema'],
            fields[field]['dataset_responsable'],
            fields[field]['dataset_fuente'],
            fields[field]['dataset_titulo'],
        )

    def zip_full_csv(self, csv_path):
        zip_file = DumpFile(task=self.task,
                            file_type=DumpFile.TYPE_ZIP,
                            file_name=DumpFile.FILENAME_FULL,
                            node=Node.objects.filter(catalog_id=self.catalog).first())
        zip_path = os.path.join(os.path.dirname(csv_path), f'{DumpFile.FILENAME_FULL}.{DumpFile.TYPE_ZIP}')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_name:
            zip_name.write(csv_path, arcname=f'{DumpFile.FILENAME_FULL}.{DumpFile.TYPE_CSV}')

        with open(zip_path, 'rb') as f:
            zip_file.file = File(f)
            zip_file.save()

        os.remove(zip_path)
