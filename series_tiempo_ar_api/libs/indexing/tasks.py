#! coding: utf-8
import json

from django.conf import settings
from django.utils import timezone
from django_rq import job, get_queue
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask, Node
from series_tiempo_ar_api.libs.indexing import constants
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer
from .database_loader import DatabaseLoader
from .scraping import Scraper


@job('indexing', timeout=settings.DISTRIBUTION_INDEX_JOB_TIMEOUT)
def index_distribution(distribution_id, node_id, task,
                       read_local=False, async=True, whitelist=False, index=settings.TS_INDEX):

    node = Node.objects.get(id=node_id)
    catalog = DataJson(json.loads(node.catalog))
    distribution = catalog.get_distribution(identifier=distribution_id)
    try:
        scraper = Scraper(read_local)
        result = scraper.run(distribution, catalog)
        if not result:
            return

        loader = DatabaseLoader(read_local=read_local, default_whitelist=whitelist)

        distribution_model = loader.run(distribution, catalog, node.catalog_id)
        if not distribution_model:
            return

        if distribution_model.dataset.indexable:
            DistributionIndexer(index=index).run(distribution_model)

    except Exception as e:
        ReadDataJsonTask.info(task, u"Excepción en distrbución {}: {}".format(distribution_id, e.message))
        raise e  # Django-rq / sentry logging

    # Si no hay más jobs encolados, la tarea se considera como finalizada
    if async and not get_queue('indexing').jobs:
        task = ReadDataJsonTask.objects.last()

        task.finished = timezone.now()
        task.status = task.FINISHED
        task.save()
        task.generate_email()

    del scraper
    del loader
