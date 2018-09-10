from django.core.files import File

from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.apps.dump.generator.dump_csv_writer import CsvDumpWriter
from .abstract_dump_gen import AbstractDumpGenerator


class ValuesCsvGenerator(AbstractDumpGenerator):

    def generate(self, filepath):
        CsvDumpWriter(self.fields, self.values_csv_row).write(filepath, constants.VALUES_HEADER)

        with open(filepath, 'rb') as f:
            self.task.dumpfile_set.create(file_name=constants.VALUES_CSV, file=File(f), task=self.task)

    @staticmethod
    def values_csv_row(value, fields, field, periodicity):
        return [
            fields[field]['dataset'].catalog.identifier,
            fields[field]['dataset'].identifier,
            fields[field]['distribution'].identifier,
            field,
            value[0].date(),  # Index
            value[1],  # value
            periodicity,
        ]
