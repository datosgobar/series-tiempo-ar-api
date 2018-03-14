#! coding: utf-8
import json

from django.conf import settings
from django_rq import job, get_queue
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask, Node, Indicator
from series_tiempo_ar_api.apps.api.models import Dataset, Catalog
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer
from .report.report_generator import ReportGenerator
from .database_loader import DatabaseLoader
from .scraping import Scraper


@job('indexing', timeout=settings.DISTRIBUTION_INDEX_JOB_TIMEOUT)
def index_distribution(distribution_id, node_id, task,
                       read_local=False, whitelist=False, index=settings.TS_INDEX):

    node = Node.objects.get(id=node_id)
    catalog = DataJson(json.loads(node.catalog))
    distribution = catalog.get_distribution(identifier=distribution_id)

    catalog_model, created = Catalog.objects.get_or_create(identifier=node.catalog_id)
    if created:
        ReadDataJsonTask.increment_indicator(task, node.catalog_id, Indicator.CATALOG_NEW)
        catalog_model.title = catalog['title']
        catalog_model.identifier = node.catalog_id
        catalog_model.save()

    dataset_model, created = Dataset.objects.get_or_create(
        identifier=distribution['dataset_identifier'],
        catalog=catalog_model,
    )

    if created:
        ReadDataJsonTask.increment_indicator(task, node.catalog_id, Indicator.DATASET_NEW)
        dataset_model.indexable = whitelist
        dataset_model.metadata = '{}'
        dataset_model.save()

    if not dataset_model.indexable:
        return

    try:
        scraper = Scraper(read_local)
        result = scraper.run(distribution, catalog)
        if not result:
            return

        loader = DatabaseLoader(task, read_local=read_local, default_whitelist=whitelist)

        distribution_model = loader.run(distribution, catalog, node.catalog_id)
        if not distribution_model:
            return

        if distribution_model.indexable:
            DistributionIndexer(index=index).run(distribution_model)

    except Exception as e:
        ReadDataJsonTask.info(task, u"Excepción en distrbución {}: {}".format(distribution_id, e.message))
        for _ in distribution['field'][1:]:
            ReadDataJsonTask.increment_indicator(task, node.catalog_id, Indicator.FIELD_ERROR)

        if settings.RQ_QUEUES['indexing'].get('ASYNC', True):
            raise e  # Django-rq / sentry logging


# Para correr con el scheduler
def scheduler():
    task = ReadDataJsonTask.objects.last()
    if task.status == task.FINISHED:
        return

    if not get_queue('indexing').jobs:
        ReportGenerator(task).generate()
