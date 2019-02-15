from django.conf import settings
from django_datajsonar.models import Distribution
from django_rq import job

from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer


@job('indexing', timeout=settings.DISTRIBUTION_INDEX_JOB_TIMEOUT)
def reindex_distribution(distribution: Distribution):
    DistributionIndexer(index=settings.TS_INDEX).reindex(distribution)
