import os

from django.test import TestCase
from django_datajsonar.models import Node

from series_tiempo_ar_api.libs.datajsonar_repositories.NodeRepository import NodeRepository


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class NodeRepositoryTests(TestCase):

    def test_read_catalog_returns_catalog_with_distributions(self):

        node = Node.objects.create(catalog_id='my catalog',
                                   catalog_url=os.path.join(SAMPLES_DIR, 'test_catalog.json'),
                                   indexable=True)

        catalog = NodeRepository(node).read_catalog()
        self.assertTrue(catalog.get_distributions())
