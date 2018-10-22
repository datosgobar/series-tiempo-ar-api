#!coding=utf8
import logging
from django_rq import job

from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask
from series_tiempo_ar_api.apps.dump.writer import Writer
from series_tiempo_ar_api.apps.dump.generator.sql.generator import SQLGenerator
from .generator.generator import DumpGenerator
from .generator.xlsx import generator


logger = logging.Logger(__name__)


@job('default', timeout='2h')
def enqueue_dump_task(task: GenerateDumpTask):
    task_choices = {
        GenerateDumpTask.TYPE_CSV: write_csv,
        GenerateDumpTask.TYPE_XLSX: write_xlsx,
        GenerateDumpTask.TYPE_SQL: write_sql,
    }

    task.refresh_from_db()
    task_choices[task.file_type](task.id)


@job('default', timeout='2h')
def write_csv(task_id, catalog=None):
    Writer('CSV', lambda task, catalog_id: DumpGenerator(task, catalog_id).generate(),
           write_csv,
           task_id,
           catalog).write()


@job('default', timeout='2h')
def write_xlsx(task_id, catalog=None):
    Writer('XLSX', generator.generate, write_xlsx, task_id, catalog).write()


# Funciones callable sin argumentos para rqscheduler
def enqueue_write_csv_task():
    task = GenerateDumpTask.objects.create(file_type=GenerateDumpTask.TYPE_CSV)
    write_csv.delay(task.id)


def enqueue_write_xlsx_task():
    task = GenerateDumpTask.objects.create(file_type=GenerateDumpTask.TYPE_XLSX)
    write_xlsx.delay(task.id)


@job('default', timeout='2h')
def write_sql(task_id, catalog=None):
    Writer('SQL',
           lambda task, catalog_id: SQLGenerator(task_id, catalog_id).generate(),
           write_sql,
           task_id,
           catalog).write()


def enqueue_write_sql_task():
    task = GenerateDumpTask.objects.create(file_type=GenerateDumpTask.TYPE_SQL)
    write_sql.delay(task.id)
