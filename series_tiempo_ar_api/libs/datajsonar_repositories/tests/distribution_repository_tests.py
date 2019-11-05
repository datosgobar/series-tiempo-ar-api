import json
import os

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from nose.tools import raises
from django_datajsonar.models import Node, Distribution, Catalog

from series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository import DistributionRepository
from series_tiempo_ar_api.libs.indexing import constants
from series_tiempo_ar_api.libs.utils.utils import parse_catalog

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class DistributionRepositoryTests(TestCase):

    def setUp(self) -> None:
        url = 'http://localhost:3456/series_tiempo_ar_api/libs/datajsonar_repositories/tests/samples/test_catalog.json'
        self.node = Node.objects.create(catalog_id='repo_test_catalog', indexable=True,
                                        catalog_url=url)
        catalog = Catalog.objects.create(metadata='{}', identifier=self.node.catalog_id)
        dataset = catalog.dataset_set.create(metadata='{}')
        self.distribution = dataset.distribution_set.create(metadata='{}', identifier='1', present=True)

    def test_get_time_index(self):
        time_index_field = self.distribution.field_set \
            .create(metadata=json.dumps({constants.SPECIAL_TYPE: constants.TIME_INDEX}))

        self.assertEqual(DistributionRepository(self.distribution).get_time_index_series(), time_index_field)

    @raises(ObjectDoesNotExist)
    def test_get_time_index_none_exists(self):
        DistributionRepository(self.distribution).get_time_index_series()

    def test_get_node(self):
        self.assertEqual(DistributionRepository(self.distribution).get_node(), self.node)

    def test_get_data_json(self):
        data_json = DistributionRepository(self.distribution).get_data_json()
        self.assertTrue(data_json.get_distributions())

    def test_read_csv_as_dataframe(self):
        parse_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'test_catalog.json'))
        distribution = Distribution.objects.last()
        df = DistributionRepository(distribution).read_csv_as_time_series_dataframe()
        self.assertTrue(list(df.columns))

    def test_get_errored_distributions_is_empty_if_all_ok(self):
        parse_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'test_catalog.json'))

        self.assertFalse(DistributionRepository.get_all_errored())

    def test_get_errored_distributions(self):
        parse_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'test_catalog.json'))
        Distribution.objects.filter(dataset__catalog__identifier='test_catalog'). \
            update(error=True, error_msg="Error!")

        self.assertEqual(DistributionRepository.get_all_errored().first().error_msg, "Error!")

    @raises(ObjectDoesNotExist)
    def test_non_present_time_index(self):
        self.distribution.field_set \
            .create(metadata=json.dumps({constants.SPECIAL_TYPE: constants.TIME_INDEX}), present=False)

        DistributionRepository(self.distribution).get_time_index_series()

    def test_multiple_indices_returns_present_if_distribution_is_presesnt(self):
        self.distribution.field_set \
            .create(metadata=json.dumps({constants.SPECIAL_TYPE: constants.TIME_INDEX}), present=False)
        index = self.distribution.field_set \
            .create(metadata=json.dumps({constants.SPECIAL_TYPE: constants.TIME_INDEX}), present=True)

        self.assertEqual(DistributionRepository(self.distribution).get_time_index_series(), index)

    def test_multiple_indices_returns_last_if_distribution_is_not_present(self):
        self.distribution.field_set \
            .create(metadata=json.dumps({constants.SPECIAL_TYPE: constants.TIME_INDEX}), present=False)
        last = self.distribution.field_set \
            .create(metadata=json.dumps({constants.SPECIAL_TYPE: constants.TIME_INDEX}), present=False)
        self.distribution.present = False
        self.assertEqual(DistributionRepository(self.distribution).get_time_index_series(), last)
