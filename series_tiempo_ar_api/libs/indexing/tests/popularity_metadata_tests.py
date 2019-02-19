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

    def test_metadata_is_created(self, mock_hits, *_):
        mock_hits.return_value = self.faker.pyint()
        update_popularity_metadata(self.distribution)

        hits = int(meta_keys.get(self.field, meta_keys.HITS_TOTAL))
        self.assertEqual(hits, mock_hits.return_value)

    def test_metadata_is_updated(self, mock_hits, *_):
        first_value = self.faker.pyint()
        mock_hits.return_value = first_value
        update_popularity_metadata(self.distribution)

        updated_value = self.faker.pyint()
        mock_hits.return_value = updated_value
        update_popularity_metadata(self.distribution)

        hits = int(meta_keys.get(self.field, meta_keys.HITS_TOTAL))
        self.assertEqual(hits, updated_value)

    def test_all_metadata_created(self, mock_hits, *_):
        mock_hits.return_value = self.faker.pyint()
        update_popularity_metadata(self.distribution)

        self.assertTrue(meta_keys.get(self.field, meta_keys.HITS_30_DAYS))
        self.assertTrue(meta_keys.get(self.field, meta_keys.HITS_90_DAYS))
        self.assertTrue(meta_keys.get(self.field, meta_keys.HITS_180_DAYS))
        self.assertTrue(meta_keys.get(self.field, meta_keys.HITS_TOTAL))
