import os

from django.core.files import File
from xlsxwriter.workbook import Workbook

from series_tiempo_ar_api.apps.dump.generator.generator import remove_old_dumps
from series_tiempo_ar_api.apps.dump.models import DumpFile, GenerateDumpTask
from series_tiempo_ar_api.utils import read_file_as_csv


class XLSXWriter:
    frequency_col = 'indice_tiempo_frecuencia'

    def __init__(self, task: GenerateDumpTask, dump_file: DumpFile):
        self.task = task
        self.csv_dump_file = dump_file
        self.header_row = None
        self.frequency_index = None
        self.worksheets = {}

    def write(self):
        try:
            self.csv_to_xlsx()
        except Exception as e:
            catalog = self.csv_dump_file.node or 'global'
            msg = f"Error escribiendo dump XLSX de dump {catalog} {self.csv_dump_file.file_name}: {e.__class__}: {e}"
            GenerateDumpTask.info(self.task, msg)

    def csv_to_xlsx(self):
        """Escribe el dump en XLSX en un archivo temporal, luego lo guarda en el storage,
        por último borra el archivo temporal. Se debe hacer así porque """
        xlsx = self.xlsx_file_name()
        workbook = Workbook(xlsx)
        sheet_count = 0
        with self.csv_dump_file.file as f:
            reader = read_file_as_csv(f)
            self.parse_header_row(next(reader))
            for r, row in enumerate(reader):
                if sheet_count > 1000000:
                    sheet_count = 0

                frequency = row[self.frequency_index]
                for c, col in enumerate(row):
                    worksheet = self.worksheets[frequency]
                    worksheet['sheet'].write(worksheet['row'], c, col)

                sheet_count += 1
        workbook.close()

        with open(xlsx, 'rb') as f:
            self.task.dumpfile_set.create(file_name=self.csv_dump_file.file_name,
                                          file_type=DumpFile.TYPE_XLSX,
                                          node=self.csv_dump_file.node,
                                          file=File(f))

        os.remove(xlsx)

    def xlsx_file_name(self):
        return f'{self.csv_dump_file.file_name}-{self.csv_dump_file.id}.{DumpFile.TYPE_XLSX}'

    def parse_header_row(self, header: list):
        self.header_row = header
        for i, col_name in enumerate(self.header_row):
            if col_name == self.frequency_col:
                self.frequency_index = i
                break

    def init_worksheet(self, workbook: Workbook, frequency: str):
        names = {
            'R/P1Y': 'anual',
            'R/P6M': 'semestral',
            'R/P3M': 'trimestral',
            'R/P1M': 'mensual',
            'R/P1D': 'diaria',
        }
        worksheet = workbook.add_worksheet(names[frequency])
        worksheet.write_row(self.header_row)
        self.worksheets[frequency] = {
            'sheet': worksheet,
            'row': 0,
        }
        return worksheet

def generate(task: GenerateDumpTask, node: str = None):
    for dump in DumpFile.get_last_of_type(DumpFile.TYPE_CSV, node):
        XLSXWriter(task, dump).write()

    for filename, _ in DumpFile.FILENAME_CHOICES:
        remove_old_dumps(filename, DumpFile.TYPE_CSV, node)
