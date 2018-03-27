#! coding: utf-8
import json

from django.conf import settings
from django_rq import job, get_queue
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask, Node, Indicator
from series_tiempo_ar_api.apps.api.models import Dataset, Catalog
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer
from series_tiempo_ar_api.libs.indexing.report.indicators import IndicatorLoader
from .report.report_generator import ReportGenerator
from .database_loader import DatabaseLoader
from .scraping import Scraper


@job('indexing', timeout=settings.DISTRIBUTION_INDEX_JOB_TIMEOUT)
def index_distribution(distribution_id, node_id, task,
                       read_local=False, whitelist=False, index=settings.TS_INDEX):

    node = Node.objects.get(id=node_id)
    catalog = DataJson(json.loads(node.catalog))
    distribution = catalog.get_distribution(identifier=distribution_id)
    dataset_model = get_dataset(catalog, node.catalog_id, distribution['dataset_identifier'], whitelist)
    if not dataset_model.indexable:
        return

    try:
        result = Scraper(read_local).run(distribution, catalog)
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
        indicator_loader = IndicatorLoader()
        indicator_loader.increment_indicator(node.catalog_id, Indicator.DISTRIBUTION_ERROR)
        indicator_loader.increment_indicator(node.catalog_id,
                                             Indicator.FIELD_ERROR,
                                             amt=len(distribution['field'][1:]))
        # No usamos un contador manejado por el indicator_loader para asegurarse que los datasets
        # sean contados una única vez (pueden fallar una vez por cada una de sus distribuciones)
        dataset_model.error = True
        dataset_model.save()

        if settings.RQ_QUEUES['indexing'].get('ASYNC', True):
            raise e  # Django-rq / sentry logging


def get_dataset(catalog, catalog_id, dataset_id, whitelist):
    catalog_model, created = Catalog.objects.get_or_create(identifier=catalog_id)
    if created:
        IndicatorLoader().increment_indicator(catalog_id, Indicator.CATALOG_NEW)
        catalog_model.title = catalog['title']
        catalog_model.identifier = catalog_id
        catalog_model.save()

    dataset_model, created = Dataset.objects.get_or_create(
        identifier=dataset_id,
        catalog=catalog_model,
    )

    if created:
        IndicatorLoader().increment_indicator(catalog_id, Indicator.DATASET_NEW)
        dataset_model.indexable = whitelist
        dataset_model.metadata = '{}'

    dataset_model.present = True
    dataset_model.save()
    return dataset_model


# Para correr con el scheduler
def scheduler():
    task = ReadDataJsonTask.objects.last()
    if task.status == task.FINISHED:
        return

    if not get_queue('indexing').jobs:
        ReportGenerator(task).generate()

    elastic = ElasticInstance.get()
    elastic.indices.forcemerge(index=settings.TS_INDEX)
