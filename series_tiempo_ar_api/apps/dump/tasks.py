#!coding=utf8

from django.utils import timezone
from django_rq import job
from .models import CSVDumpTask
from .csv import CSVDumpGenerator


@job('default', timeout=0)
def dump_db_to_csv(task_id):
    task = CSVDumpTask.objects.get(id=task_id)
    try:
        csv_gen = CSVDumpGenerator(task)
        csv_gen.generate()
    except Exception as e:
        CSVDumpTask.info(task, str(e))

    task.status = task.FINISHED
    task.finished = timezone.now()
    task.save()


def enqueue_csv_task(task=None):
    if task is None:
        task = CSVDumpTask()
        task.save()

    dump_db_to_csv.delay(task.id)
