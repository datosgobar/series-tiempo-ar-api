from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.apps.dump.models import DumpFile, ZipDumpFile
from .abstract_dump_gen import AbstractDumpGenerator
from .dump_csv_writer import CsvDumpWriter


class FullCsvGenerator(AbstractDumpGenerator):
    filename = DumpFile.FILENAME_FULL

    def generate(self):
        filepath = self.get_file_path()
        CsvDumpWriter(self.task, self.fields, self.full_csv_row).write(filepath, constants.FULL_CSV_HEADER)

        self.write(filepath, DumpFile.FILENAME_FULL, zip_file=True)

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
