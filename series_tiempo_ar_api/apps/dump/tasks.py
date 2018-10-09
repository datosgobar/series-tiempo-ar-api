#!coding=utf8
import logging
from django_rq import job

from series_tiempo_ar_api.apps.dump.writer import Writer
from .generator.generator import DumpGenerator
from .generator.xlsx import generator


logger = logging.Logger(__name__)


@job('default', timeout='2h')
def write_csv(task_id, catalog=None):
    Writer('CSV', lambda task, catalog_id: DumpGenerator(task, catalog_id).generate(),
           write_csv,
           task_id,
           catalog).write()


def enqueue_csv_dump_task(task=None):
    write_csv.delay(task)


@job('default', timeout='2h')
def write_xlsx(task_id, catalog=None):
    Writer('XLSX', generator.generate, write_xlsx, task_id, catalog).write()


def enqueue_xlsx_dump_task(task=None):
    write_xlsx.delay(task)
