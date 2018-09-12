import os
import zipfile

from django.core.files import File

from series_tiempo_ar_api.apps.dump import constants
from .abstract_dump_gen import AbstractDumpGenerator
from .dump_csv_writer import CsvDumpWriter


class FullCsvGenerator(AbstractDumpGenerator):

    def generate(self, filepath):
        CsvDumpWriter(self.task, self.fields, self.full_csv_row).write(filepath, constants.FULL_CSV_HEADER)

        with open(filepath, 'rb') as f:
            self.task.dumpfile_set.create(file_name=constants.FULL_CSV, file=File(f), task=self.task)

        self.zip_full_csv(filepath, os.path.join(os.path.dirname(filepath), constants.FULL_CSV_ZIPPED))

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

    def zip_full_csv(self, csv_path, zip_path):
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_name:
            zip_name.write(csv_path, arcname=constants.FULL_CSV)

        with open(zip_path, 'rb') as f:
            self.task.dumpfile_set.create(file_name=constants.FULL_CSV_ZIPPED,
                                          file=File(f))

        os.remove(zip_path)
