#!coding=utf8
import logging
from traceback import format_exc

from django.utils import timezone
from django.conf import settings
from django_rq import job, get_queue
from django_datajsonar.models import Node

from .models import CSVDumpTask
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


class Writer:

    def __init__(self, tag: str, action: callable, recursive_task: callable, task: int = None, catalog: str = None):
        self.tag = tag
        self.action = action
        self.recursive_task = recursive_task
        self.catch_exceptions = getattr(settings, 'DUMP_LOG_EXCEPTIONS', True)

        self.task = CSVDumpTask.objects.get(id=task) if task is not None else CSVDumpTask.objects.create()
        self.catalog_id = catalog

    def write(self):
        if self.catalog_id is None:
            nodes = Node.objects.filter(indexable=True).values_list('catalog_id', flat=True)
            for node in nodes:
                self.recursive_task.delay(self.task.id, node)
        if self.catch_exceptions:
            self.run_catching_exceptions()
        else:
            self.action(self.task, self.catalog_id)

        async = settings.RQ_QUEUES['default'].get('ASYNC', True)
        finish = not async or (async and not get_queue('default').count)

        if finish:
            self.task.refresh_from_db()
            self.task.status = self.task.FINISHED
            self.task.finished = timezone.now()
            self.task.save()

    def run_catching_exceptions(self):
        try:
            self.action(self.task, self.catalog_id)
        except Exception as e:
            exc = str(e) or format_exc(e)
            msg = f"{self.catalog_id or 'global'}: Error generando el dump {self.tag}: {exc}"
            logger.error(msg)
            CSVDumpTask.info(self.task, msg)
