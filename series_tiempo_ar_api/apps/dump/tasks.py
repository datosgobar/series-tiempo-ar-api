#!coding=utf8
from traceback import format_exc

from django.utils import timezone
from django_rq import job
from .models import CSVDumpTask
from .generator.csv import DumpGenerator


@job('default', timeout=0)
def dump_db_to_csv(task_id):
    task = CSVDumpTask.objects.get(id=task_id)
    try:
        csv_gen = DumpGenerator(task)
        csv_gen.generate()
    except Exception as e:
        msg = "Error generando el dump: {}".format(str(e) or format_exc(e))
        CSVDumpTask.info(task, msg)

    task.status = task.FINISHED
    task.finished = timezone.now()
    task.save()


def enqueue_csv_dump_task(task=None):
    if task is None:
        task = CSVDumpTask.objects.create()

    dump_db_to_csv.delay(task.id)
