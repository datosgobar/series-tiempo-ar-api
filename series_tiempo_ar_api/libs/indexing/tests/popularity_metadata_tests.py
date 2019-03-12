from unittest import TestCase

import faker
import mock
from django_datajsonar.models import Distribution, Catalog, Dataset

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.indexing.popularity import update_popularity_metadata


@mock.patch('series_tiempo_ar_api.libs.indexing.popularity.popularity_aggregation')
@mock.patch('series_tiempo_ar_api.libs.indexing.popularity.Index')
@mock.patch('series_tiempo_ar_api.libs.indexing.popularity.get_hits')
class PopularityTests(TestCase):
    faker = faker.Faker()

    @classmethod
    def setUpClass(cls):
        super(PopularityTests, cls).setUpClass()
        catalog = Catalog.objects.create(identifier='test_catalog')
        dataset = Dataset.objects.create(catalog=catalog)
        cls.distribution = Distribution.objects.create(dataset=dataset, identifier='test_distribution')

        cls.field = cls.distribution.field_set.create(identifier='test_field')
        cls.field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='true')

    def test_metadata_is_created(self, mock_hits, *_):
        mock_value = self._update_popularity_metadata(mock_hits)

        hits = int(meta_keys.get(self.field, meta_keys.HITS_TOTAL))
        self.assertEqual(hits, mock_value)

    def test_metadata_is_updated(self, mock_hits, *_):
        self._update_popularity_metadata(mock_hits)

        updated_value = self._update_popularity_metadata(mock_hits)

        hits = int(meta_keys.get(self.field, meta_keys.HITS_TOTAL))
        self.assertEqual(hits, updated_value)

    def test_all_metadata_created(self, mock_hits, *_):
        self._update_popularity_metadata(mock_hits)

        self.assertTrue(meta_keys.get(self.field, meta_keys.HITS_30_DAYS))
        self.assertTrue(meta_keys.get(self.field, meta_keys.HITS_90_DAYS))
        self.assertTrue(meta_keys.get(self.field, meta_keys.HITS_180_DAYS))
        self.assertTrue(meta_keys.get(self.field, meta_keys.HITS_TOTAL))

    def _update_popularity_metadata(self, mock_hits):
        mock_value = self.faker.pyint()
        mock_hits.return_value = mock_value
        update_popularity_metadata(self.distribution)
        return mock_value
