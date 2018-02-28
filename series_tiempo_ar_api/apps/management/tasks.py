#! coding: utf-8

from django.utils import timezone
from django_rq import job, get_queue
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.actions import DatasetIndexableToggler
from series_tiempo_ar_api.apps.management.models import Node, DatasetIndexingFile, ReadDataJsonTask
from series_tiempo_ar_api.apps.management.strings import FILE_READ_ERROR, READ_ERROR
from series_tiempo_ar_api.libs.indexing.tasks import index_distribution

@job('indexing')
def read_datajson(task, async=True, whitelist=False, read_local=False):
    """Tarea raíz de indexación. Itera sobre todos los nodos indexables (federados) e
    inicia la tarea de indexación sobre cada uno de ellos
    """
    nodes = Node.objects.filter(indexable=True)
    task.status = task.RUNNING

    for node in nodes:
        catalog_id = node.catalog_id
        catalog_url = node.catalog_url
        try:
            catalog = DataJson(catalog_url)
        except Exception as e:
            ReadDataJsonTask.info(task, READ_ERROR.format(catalog_id, e.message))
            continue

        for distribution in catalog.get_distributions(only_time_series=True):
            fake_catalog = catalog.copy()
            fake_catalog['dataset'] = filter(
                lambda x: x['identifier'] != distribution['dataset_identifier'],
                fake_catalog['dataset']
            )
            if async:
                index_distribution.delay(distribution,
                                         fake_catalog,
                                         catalog_id,
                                         task,
                                         read_local=read_local,
                                         whitelist=whitelist)
            else:
                index_distribution(distribution,
                                   fake_catalog,
                                   catalog_id,
                                   task,
                                   read_local=read_local,
                                   async=False,
                                   whitelist=whitelist)

    # Caso de no hay nodos o todos dieron error, marco como finalizado
    if not nodes or (async and not get_queue('indexing').jobs):
        task.status = task.FINISHED
        task.save()


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
