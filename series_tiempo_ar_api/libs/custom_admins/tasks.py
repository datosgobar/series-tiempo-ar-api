from django.conf import settings
from django_datajsonar.models import Distribution

from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer


def reindex_distribution(distribution: Distribution):
    DistributionIndexer(index=settings.TS_INDEX).reindex(distribution)
