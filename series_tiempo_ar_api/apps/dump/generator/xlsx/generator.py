import os

from django.core.files import File

from series_tiempo_ar_api.apps.dump.generator.xlsx.workbook import DumpWorkbook
from series_tiempo_ar_api.apps.dump.models import DumpFile, GenerateDumpTask
from series_tiempo_ar_api.utils import read_file_as_csv


class XLSXWriter:
    multiple_sheets = {
        DumpFile.FILENAME_VALUES: True,
        DumpFile.FILENAME_FULL: True,
        DumpFile.FILENAME_METADATA: False,
        DumpFile.FILENAME_SOURCES: False,
    }

    def __init__(self, task: GenerateDumpTask, dump_file: DumpFile, workbook_class=DumpWorkbook):
        self.workbook_class = workbook_class
        self.task = task
        self.csv_dump_file = dump_file
        self.frequency_column_index = None
        self.worksheets = {}

    def write(self):
        try:
            self.csv_to_xlsx()
        except IOError as e:
            catalog = self.csv_dump_file.node or 'global'
            msg = f"Error escribiendo dump XLSX de dump {catalog} {self.csv_dump_file.file_name}: {e.__class__}: {e}"
            GenerateDumpTask.info(self.task, msg)

    def csv_to_xlsx(self):
        """Escribe el dump en XLSX en un archivo temporal, luego lo guarda en el storage,
        por último borra el archivo temporal. Se debe hacer así para hacer un "upload" al
        storage distribuido.
        """
        xlsx = self.xlsx_file_name()
        with self.csv_dump_file.file as f:
            reader = read_file_as_csv(f)
            header_row = next(reader)

            workbook = self.workbook_class(xlsx,
                                           header_row=header_row,
                                           split_by_frequency=self.multiple_sheets[self.csv_dump_file.file_name])

            for row in reader:
                workbook.write_row(row)

        workbook.close()

        with open(xlsx, 'rb') as f:
            self.task.dumpfile_set.create(file_name=self.csv_dump_file.file_name,
                                          file_type=DumpFile.TYPE_XLSX,
                                          node=self.csv_dump_file.node,
                                          file=File(f))

        os.remove(xlsx)

    def xlsx_file_name(self):
        node = self.csv_dump_file.node or 'global'
        name = self.csv_dump_file.file_name
        return f'{node}-{name}-{self.csv_dump_file.id}.{DumpFile.TYPE_XLSX}'


def generate(task: GenerateDumpTask, node: str = None, workbook_class=DumpWorkbook):
    for dump in DumpFile.get_last_of_type(DumpFile.TYPE_CSV, node):
        XLSXWriter(task, dump, workbook_class).write()
