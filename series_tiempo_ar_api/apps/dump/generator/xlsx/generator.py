import csv
import io

from xlsxwriter.workbook import Workbook

from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.apps.dump.models import DumpFile, CSVDumpTask


def read_file_as_csv(file):
    ios = io.StringIO()
    ios.write(file.read().decode('utf-8'))

    ios.seek(0)
    reader = csv.reader(ios)
    return reader


def csv_to_xlsx(dump_file: DumpFile):
    workbook = Workbook(f'{dump_file.file_name}-{dump_file.id}.xlsx')
    worksheet = workbook.add_worksheet()
    sheet_count = 0
    with dump_file.file as f:
        reader = read_file_as_csv(f)
        for r, row in enumerate(reader):
            if sheet_count > 1000000:
                worksheet = workbook.add_worksheet()
                sheet_count = 0

            for c, col in enumerate(row):
                worksheet.write(sheet_count, c, col)

            sheet_count += 1
    workbook.close()


def generate(task: CSVDumpTask, node: str = None):
    dumps_qs = DumpFile.objects.all()
    if node:
        dumps_qs = dumps_qs.filter(node__catalog_id=node)

    dumps = []
    for dump_name in DumpFile.FILENAME_CHOICES:
        dump_file = dumps_qs.filter(file_name=dump_name).last()
        if dump_file is not None:
            dumps.append(dump_file)

    for dump in dumps:
        try:
            csv_to_xlsx(dump)
        except IOError as e:
            CSVDumpTask.info(task, f"Error escribiendo dump XLSX de dump {dump.file_name}: {e.__class__}: {e}")
