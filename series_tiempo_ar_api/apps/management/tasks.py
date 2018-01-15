#! coding: utf-8

from django.utils import timezone
from django_rq import job

from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.actions import DatasetIndexableToggler
from series_tiempo_ar_api.apps.management.models import Node, DatasetIndexingFile, ReadDataJsonTask
from series_tiempo_ar_api.apps.api.indexing import catalog_reader
from series_tiempo_ar_api.apps.management.strings import FILE_READ_ERROR, READ_ERROR


@job('indexing')
def read_datajson(task, async=True):
    task_id = task.id
    nodes = Node.objects.filter(indexable=True)
    task.status = task.RUNNING
    task.catalogs.add(*[node.id for node in nodes])
    task.save()
    logs = []

    for node in nodes:
        catalog_id = node.catalog_id
        catalog_url = node.catalog_url
        try:
            DataJson(catalog_url)
            if not async:
                start_index_catalog(catalog_id, catalog_url, task_id)
            else:
                start_index_catalog.delay(catalog_id, catalog_url, task_id)
        except (IOError, ValueError, AssertionError) as e:
            logs.append(READ_ERROR.format(catalog_id, e))

        logs_string = ''
        for log in logs:
            logs_string += log + '\n'

        task = ReadDataJsonTask.objects.get(id=task_id)
        task.logs = logs_string
        task.save()

    if not nodes:
        task.status = task.FINISHED
        task.save()


@job('indexing', timeout=1500)
def start_index_catalog(catalog_id, catalog_url, task_id):
    task = ReadDataJsonTask.objects.get(id=task_id)
    task.catalogs.remove(Node.objects.get(catalog_id=catalog_id))
    if not task.catalogs.count():
        task.status = task.INDEXING
        task.finished = timezone.now()

        task.save()

    catalog_reader.index_catalog(catalog_url, catalog_id, task=task)


@job('indexing')
def bulk_index(indexing_file_id):
    indexing_file_model = DatasetIndexingFile.objects.get(id=indexing_file_id)
    toggler = DatasetIndexableToggler()
    try:
        logs_list = toggler.process(indexing_file_model.indexing_file)
        logs = ''
        for log in logs_list:
            logs += log + '\n'

        state = DatasetIndexingFile.PROCESSED
    except ValueError:
        logs = FILE_READ_ERROR
        state = DatasetIndexingFile.FAILED

    indexing_file_model.state = state
    indexing_file_model.logs = logs
    indexing_file_model.modified = timezone.now()
    indexing_file_model.save()
