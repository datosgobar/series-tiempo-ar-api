import csv
import io
import os

from django.core.files import File
from xlsxwriter.workbook import Workbook

from series_tiempo_ar_api.apps.dump.generator.generator import remove_old_dumps
from series_tiempo_ar_api.apps.dump.models import DumpFile, GenerateDumpTask


def read_file_as_csv(file):
    ios = io.StringIO()
    ios.write(file.read().decode('utf-8'))

    ios.seek(0)
    reader = csv.reader(ios)
    return reader


def csv_to_xlsx(dump_file: DumpFile):
    xlsx = f'{dump_file.file_name}-{dump_file.id}.xlsx'
    workbook = Workbook(xlsx)
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

    with open(xlsx, 'rb') as f:
        dump_file.task.dumpfile_set.create(file_name=dump_file.file_name,
                                           file_type=DumpFile.TYPE_XLSX,
                                           node=dump_file.node,
                                           file=File(f))

    os.remove(xlsx)


def generate(task: GenerateDumpTask, node: str = None):
    dumps_qs = DumpFile.objects.all()
    if node:
        dumps_qs = dumps_qs.filter(node__catalog_id=node)

    dumps = []
    for dump_name, _ in DumpFile.FILENAME_CHOICES:
        dump_file = dumps_qs.filter(file_name=dump_name, file_type=DumpFile.TYPE_CSV).last()
        if dump_file is not None:
            dumps.append(dump_file)

    for dump in dumps:
        try:
            csv_to_xlsx(dump)
        except Exception as e:
            catalog = node or 'global'
            msg = f"Error escribiendo dump XLSX de dump {catalog} {dump.file_name}: {e.__class__}: {e}"
            GenerateDumpTask.info(task, msg)

    for filename, _ in DumpFile.FILENAME_CHOICES:
        remove_old_dumps(filename, DumpFile.TYPE_CSV, node)
