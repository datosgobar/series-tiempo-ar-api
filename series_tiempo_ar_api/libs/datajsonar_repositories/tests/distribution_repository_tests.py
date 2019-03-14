import json

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django_datajsonar.models import Distribution, Catalog
from nose.tools import raises

from series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository import DistributionRepository
from series_tiempo_ar_api.libs.indexing import constants


class DistributionRepositoryTests(TestCase):

    def test_get_time_index(self):
        Catalog.objects.all().delete()
        catalog = Catalog.objects.create()
        dataset = catalog.dataset_set.create()

        distribution = Distribution.objects.create(dataset=dataset)
        time_index_series = distribution.field_set.create(metadata=json.dumps({constants.SPECIAL_TYPE: constants.TIME_INDEX}))

        self.assertEqual(DistributionRepository(distribution).get_time_index_series().id, time_index_series.id)

    @raises(ObjectDoesNotExist)
    def test_get_time_index_none_exists(self):
        Catalog.objects.all().delete()
        catalog = Catalog.objects.create()
        dataset = catalog.dataset_set.create()

        distribution = Distribution.objects.create(dataset=dataset)
        distribution.field_set.create(metadata=json.dumps({constants.SPECIAL_TYPE: 'not a time index'}))
        DistributionRepository(distribution).get_time_index_series()
