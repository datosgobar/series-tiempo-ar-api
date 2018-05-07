#! coding: utf-8
import json
from traceback import format_exc

from django.conf import settings
from django.db import transaction
from django_rq import job, get_queue
from pydatajson import DataJson

from django_datajsonar.models import Node
from django_datajsonar.models import Distribution
from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask, Indicator
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer
from series_tiempo_ar_api.libs.indexing.report.indicators import IndicatorLoader
from .report.report_generator import ReportGenerator
from .scraping import Scraper


@job('indexing', timeout=settings.DISTRIBUTION_INDEX_JOB_TIMEOUT)
def index_distribution(distribution_id, node_id, task_id,
                       read_local=False, whitelist=False, index=settings.TS_INDEX):

    node = Node.objects.get(id=node_id)
    task = ReadDataJsonTask.objects.get(id=task_id)
    catalog = DataJson(json.loads(node.catalog))
    distribution = catalog.get_distribution(identifier=distribution_id)
    distribution_model = Distribution.objects.get(identifier=distribution_id)
    if not distribution_model.dataset.indexable:
        return

    try:
        result = Scraper(read_local).run(distribution, catalog)
        if not result:
            return

        if distribution_model.dataset.indexable:
            DistributionIndexer(index=index).run(distribution_model)

    except Distribution.DoesNotExist as e:
        _handle_exception(distribution_model.dataset, distribution, distribution_id, e, node, task)


def _handle_exception(dataset_model, distribution, distribution_id, exc, node, task):
    msg = u"Excepción en distrbución {} del catálogo {}: {}"
    if exc:
        e_msg = exc
    else:
        e_msg = format_exc()
    msg = msg.format(distribution_id, node.catalog_id, e_msg)
    ReadDataJsonTask.info(task, msg)
    indicator_loader = IndicatorLoader()
    indicator_loader.increment_indicator(node.catalog_id, Indicator.DISTRIBUTION_ERROR)
    indicator_loader.increment_indicator(node.catalog_id,
                                         Indicator.FIELD_ERROR,
                                         amt=len(distribution['field'][1:]))

    with transaction.atomic():
        try:
            distribution = Distribution.objects.get(identifier=distribution_id)
            distribution.error = msg
            distribution.save()
        except Distribution.DoesNotExist:
            pass

    # No usamos un contador manejado por el indicator_loader para asegurarse que los datasets
    # sean contados una única vez (pueden fallar una vez por cada una de sus distribuciones)
    dataset_model.error = True
    dataset_model.save()

    dataset_model.catalog.error = True
    dataset_model.catalog.save()

    if settings.RQ_QUEUES['indexing'].get('ASYNC', True):
        raise exc  # Django-rq / sentry logging


# Para correr con el scheduler
def scheduler():
    task = ReadDataJsonTask.objects.last()
    if task.status == task.FINISHED:
        return

    if not get_queue('indexing').jobs:
        ReportGenerator(task).generate()

    elastic = ElasticInstance.get()
    if elastic.indices.exists(index=settings.TS_INDEX):
        elastic.indices.forcemerge(index=settings.TS_INDEX)
