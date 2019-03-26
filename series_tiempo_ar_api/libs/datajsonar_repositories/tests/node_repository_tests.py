import os

import mock
from django.test import TestCase

from series_tiempo_ar_api.libs.datajsonar_repositories.NodeRepository import NodeRepository


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class NodeRepositoryTests(TestCase):

    def test_read_catalog_returns_catalog_with_distributions(self):
        node = mock.Mock(catalog_url=os.path.join(SAMPLES_DIR, 'test_catalog.json'))

        catalog = NodeRepository(node).read_catalog()
        self.assertTrue(catalog.get_distributions())
