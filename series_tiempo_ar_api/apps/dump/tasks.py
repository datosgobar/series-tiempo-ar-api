#!coding=utf8
from traceback import format_exc

from django.utils import timezone
from django.conf import settings
from django_rq import job, get_queue
from django_datajsonar.models import Node

from .models import CSVDumpTask
from .generator.generator import DumpGenerator


@job('default', timeout='2h')
def dump_db_to_csv(task_id, catalog_id: str = None):
    task = CSVDumpTask.objects.get(id=task_id)

    if catalog_id is None:
        nodes = Node.objects.filter(indexable=True).values_list('catalog_id', flat=True)
        for node in nodes:
            dump_db_to_csv.delay(task_id, node)

    try:
        csv_gen = DumpGenerator(task, catalog_id)
        csv_gen.generate()
    except Exception as e:
        exc = str(e) or format_exc(e)
        msg = f"{catalog_id or 'global'}: Error generando el dump: {exc}"
        CSVDumpTask.info(task, msg)

    finish = settings.RQ_QUEUES['default'].get('ASYNC', True) and \
        not get_queue('default').count

    if finish:
        task.refresh_from_db()
        task.status = task.FINISHED
        task.finished = timezone.now()
        task.save()


def enqueue_csv_dump_task(task=None):
    if task is None:
        task = CSVDumpTask.objects.create()

    dump_db_to_csv.delay(task.id)
