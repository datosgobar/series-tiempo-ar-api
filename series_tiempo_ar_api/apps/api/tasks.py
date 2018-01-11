#! coding: utf-8
from django.conf import settings
from django_rq import job

from .models import Distribution
from .indexing.distribution_indexer import DistributionIndexer


@job('indexing', timeout=settings.DISTRIBUTION_INDEX_JOB_TIMEOUT)
def index_distribution(index, distribution_id):
    distribution = Distribution.objects.get(id=distribution_id)

    DistributionIndexer(index=index).run(distribution)
