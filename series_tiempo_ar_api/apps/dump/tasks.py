#!coding=utf8
import logging
from django_rq import job

from series_tiempo_ar_api.apps.dump.generator.dta import DtaGenerator
from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask, DumpFile
from series_tiempo_ar_api.apps.dump.writer import Writer
from series_tiempo_ar_api.apps.dump.generator.sql.generator import SQLGenerator
from .generator.generator import DumpGenerator
from .generator.xlsx import generator


logger = logging.Logger(__name__)


@job('default', timeout='3h')
def enqueue_dump_task(task: GenerateDumpTask):
    task.save()  # Evito problemas de DoesNotExist cuando se llama async
    task_choices = {
        GenerateDumpTask.TYPE_CSV: write_csv,
        GenerateDumpTask.TYPE_XLSX: write_xlsx,
        GenerateDumpTask.TYPE_SQL: write_sql,
        GenerateDumpTask.TYPE_DTA: write_dta,
    }

    task_choices[task.file_type](task.id)


@job('default', timeout='3h')
def write_csv(task_id, catalog=None):
    Writer(DumpFile.TYPE_CSV, lambda task, catalog_id: DumpGenerator(task, catalog_id).generate(),
           write_csv,
           task_id,
           catalog).write()


@job('default', timeout='2h')
def write_xlsx(task_id, catalog=None):
    Writer(DumpFile.TYPE_XLSX, generator.generate, write_xlsx, task_id, catalog).write()


# Funciones callable sin argumentos para rqscheduler
def enqueue_write_csv_task():
    task = GenerateDumpTask.objects.create(file_type=GenerateDumpTask.TYPE_CSV)
    write_csv.delay(task.id)


def enqueue_write_xlsx_task():
    task = GenerateDumpTask.objects.create(file_type=GenerateDumpTask.TYPE_XLSX)
    write_xlsx.delay(task.id)


@job('default', timeout='2h')
def write_sql(task_id, catalog=None):
    Writer(DumpFile.TYPE_SQL,
           lambda task, catalog_id: SQLGenerator(task_id, catalog_id).generate(),
           write_sql,
           task_id,
           catalog).write()


def enqueue_write_sql_task():
    task = GenerateDumpTask.objects.create(file_type=GenerateDumpTask.TYPE_SQL)
    write_sql.delay(task.id)


@job('default', timeout='1h')
def write_dta(task_id, catalog=None):
    Writer(DumpFile.TYPE_DTA,
           lambda task, catalog_id: DtaGenerator(task_id, catalog_id).generate(),
           write_dta,
           task_id,
           catalog).write()


def enqueue_write_dta_task():
    task = GenerateDumpTask.objects.create(file_type=GenerateDumpTask.TYPE_DTA)
    write_dta.delay(task.id)
