#! coding: utf-8
from django.conf import settings
from django.utils import timezone
from django_rq import job, get_queue

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.libs.indexing import constants
from .distribution_indexer import DistributionIndexer
from .database_loader import DatabaseLoader
from .scraping import Scraper


@job('indexing', timeout=settings.DISTRIBUTION_INDEX_JOB_TIMEOUT)
def index_distribution(distribution, catalog, catalog_id, task,
                       read_local=False, async=True, whitelist=False, index=settings.TS_INDEX):

    identifier = distribution[constants.IDENTIFIER]
    try:
        scraper = Scraper(task, read_local)
        result = scraper.run(distribution, catalog)
        if not result:
            return

        loader = DatabaseLoader(task, read_local, default_whitelist=whitelist)

        distribution_model = loader.run(distribution, catalog, catalog_id)
        if not distribution_model:
            return

        if distribution_model.dataset.indexable:
            DistributionIndexer(index=index).run(distribution_model)

    except Exception as e:
        ReadDataJsonTask.info(task, u"Excepción en distrbución {}: {}".format(identifier, e.message))
        # raise e  # Django-rq / sentry logging

    # Si no hay más jobs encolados, la tarea se considera como finalizada
    if async and not get_queue('indexing').jobs:
        task = ReadDataJsonTask.objects.last()

        task.finished = timezone.now()
        task.status = task.FINISHED
        task.save()
        task.generate_email()

    ReadDataJsonTask.info(task, u"Distribución {} OK".format(identifier))