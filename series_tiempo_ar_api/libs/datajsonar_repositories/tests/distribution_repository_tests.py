import json
import os

from mock import Mock, patch
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from nose.tools import raises
from django_datajsonar.models import Node, Distribution

from series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository import DistributionRepository
from series_tiempo_ar_api.libs.indexing import constants
from series_tiempo_ar_api.libs.utils.utils import parse_catalog

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class DistributionRepositoryTests(TestCase):

    def test_get_time_index(self):
        time_index_field = Mock(metadata=json.dumps({constants.SPECIAL_TYPE: constants.TIME_INDEX}))
        distribution = Mock()
        distribution.field_set.all.return_value = [time_index_field]

        self.assertEqual(DistributionRepository(distribution).get_time_index_series(), time_index_field)

    @raises(ObjectDoesNotExist)
    def test_get_time_index_none_exists(self):
        distribution = Mock()
        distribution.field_set.all.return_value = []
        DistributionRepository(distribution).get_time_index_series()

    def test_get_node(self):
        distribution = Mock()
        distribution.dataset.catalog.identifier = 'test_node'

        node = Node(catalog_id='test_node')
        with patch('series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository.Node') as fake_node:
            fake_node.objects.get.return_value = node
            self.assertTrue(fake_node.objects.get.called_with(catalog_id='test_node'))
            self.assertEqual(DistributionRepository(distribution).get_node(), node)

    @patch('series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository.Node')
    @patch('series_tiempo_ar_api.libs.datajsonar_repositories.node_repository.NodeRepository')
    def test_get_data_json(self, repository, fake_node):
        distribution = Mock()
        node = Node(catalog_id='test_node')
        fake_node.objects.get.return_value = node
        DistributionRepository(distribution).get_data_json()
        self.assertTrue(repository.called_with(node))

    def test_read_csv_as_dataframe(self):
        time_index_title = 'indice_tiempo'
        time_index_field = Mock(metadata=json.dumps({constants.SPECIAL_TYPE: constants.TIME_INDEX}),
                                title=time_index_title)

        distribution = Mock()
        distribution.field_set.all.return_value = [time_index_field]

        csv_reader = Mock()
        DistributionRepository(distribution, csv_reader=csv_reader).read_csv_as_time_series_dataframe()
        csv_reader.assert_called_with(distribution, time_index_title)

    def test_get_errored_distributions_is_empty_if_all_ok(self):
        parse_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'test_catalog.json'))

        self.assertFalse(DistributionRepository.get_all_errored())

    def test_get_errored_distributions(self):
        parse_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'test_catalog.json'))
        Distribution.objects.filter(dataset__catalog__identifier='test_catalog'). \
            update(error=True, error_msg="Error!")

        self.assertEqual(DistributionRepository.get_all_errored().first().error_msg, "Error!")
