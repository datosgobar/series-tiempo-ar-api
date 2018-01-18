#! coding: utf-8
from django.conf import settings
from django.utils import timezone
from django_rq import job, get_queue

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from .models import Distribution
from .indexing.distribution_indexer import DistributionIndexer


@job('indexing', timeout=settings.DISTRIBUTION_INDEX_JOB_TIMEOUT)
def index_distribution(index, distribution_id):
    distribution = Distribution.objects.get(id=distribution_id)

    DistributionIndexer(index=index).run(distribution)

    # Si no hay más jobs encolados, la tarea se considera como finalizada
    if not get_queue('indexing').jobs:
        task = ReadDataJsonTask.objects.last()
        task.finished = timezone.now()
        task.status = task.FINISHED
        task.save()
        task.generate_email()
