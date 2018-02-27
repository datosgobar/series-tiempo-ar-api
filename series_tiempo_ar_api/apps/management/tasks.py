#! coding: utf-8

from django.utils import timezone
from django_rq import job, get_queue
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.actions import DatasetIndexableToggler
from series_tiempo_ar_api.apps.management.models import Node, DatasetIndexingFile, ReadDataJsonTask
from series_tiempo_ar_api.apps.management.strings import FILE_READ_ERROR, READ_ERROR
from series_tiempo_ar_api.libs.indexing import catalog_reader


@job('indexing')
def read_datajson(task, async=True, whitelist=False):
    """Tarea raíz de indexación. Itera sobre todos los nodos indexables (federados) e
    inicia la tarea de indexación sobre cada uno de ellos
    """
    task_id = task.id
    nodes = Node.objects.filter(indexable=True)
    task.status = task.RUNNING

    # Trackea los nodos a indexar
    task.catalogs.add(*[node.id for node in nodes])
    task.save()
    logs = []

    for node in nodes:
        catalog_id = node.catalog_id
        catalog_url = node.catalog_url
        try:
            DataJson(catalog_url)
            if not async:  # Debug
                start_index_catalog(catalog_id,
                                    catalog_url,
                                    task_id,
                                    async=False,
                                    whitelist=whitelist)
            else:
                start_index_catalog.delay(catalog_id, catalog_url, task_id, whitelist=whitelist)
        except Exception as e:
            logs.append(READ_ERROR.format(catalog_id, e))
            task.catalogs.remove(node)

        # Logging de errores de lectura
        logs_string = ''
        for log in logs:
            logs_string += log + '\n'

        task = ReadDataJsonTask.objects.get(id=task_id)
        task.logs = logs_string
        task.save()

    # Caso de no hay nodos o todos dieron error, marco como finalizado
    if not nodes or (async and not get_queue('indexing').jobs):
        task.status = task.FINISHED
        task.save()


@job('indexing', timeout=1500)
def start_index_catalog(catalog_id, catalog_url, task_id, async=True, whitelist=False):
    task = ReadDataJsonTask.objects.get(id=task_id)
    task.catalogs.remove(Node.objects.get(catalog_id=catalog_id))
    task.status = task.INDEXING

    task.save()

    catalog_reader.index_catalog(catalog_url,
                                 catalog_id,
                                 task=task,
                                 async=async,
                                 whitelist=whitelist)


@job('indexing')
def bulk_whitelist(indexing_file_id):
    """Marca datasets como indexables en conjunto a partir de la lectura
    del archivo la instancia del DatasetIndexingFile pasado
    """
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
