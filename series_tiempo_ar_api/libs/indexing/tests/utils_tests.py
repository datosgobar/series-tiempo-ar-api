from faker import Faker
from django.test import TestCase
from django_datajsonar.models import Catalog, Dataset, Distribution, Field

from ..indexer.utils import remove_duplicated_fields

fake = Faker()


class DuplicatedFieldsTests(TestCase):

    def setUp(self):
        catalog = Catalog.objects.create()
        dataset = Dataset.objects.create(catalog=catalog)
        self.distribution = Distribution.objects.create(dataset=dataset)

    def test_run_no_duplicated_fields(self):
        Field.objects.create(distribution=self.distribution,
                             identifier=fake.pystr(),
                             title="one_title",
                             present=True)

        remove_duplicated_fields(self.distribution)

        self.assertEqual(self.distribution.field_set.count(), 1)

    def test_run_duplicated_fields(self):
        identifier = fake.pystr()

        Field.objects.create(distribution=self.distribution,
                             identifier=identifier,
                             title="one_title",
                             present=True)
        Field.objects.create(distribution=self.distribution,
                             identifier=identifier,
                             title="other_title",
                             present=False)

        remove_duplicated_fields(self.distribution)

        self.assertEqual(self.distribution.field_set.count(), 1)

    def test_run_not_present_removes_non_present(self):
        identifier = fake.pystr()

        Field.objects.create(distribution=self.distribution,
                             identifier=identifier,
                             title="one_title",
                             present=False)
        Field.objects.create(distribution=self.distribution,
                             identifier=identifier,
                             title="other_title",
                             present=True)

        remove_duplicated_fields(self.distribution)

        self.assertTrue(self.distribution.field_set.get(identifier=identifier).present)

    def test_run_multiple_single_fields(self):
        Field.objects.create(distribution=self.distribution,
                             identifier=fake.pystr(),
                             title="one_title",
                             present=True)
        Field.objects.create(distribution=self.distribution,
                             identifier=fake.pystr(),
                             title="other_title",
                             present=True)

        remove_duplicated_fields(self.distribution)

        self.assertEqual(self.distribution.field_set.count(), 2)

    def test_run_multiple_non_present_fields(self):
        Field.objects.create(distribution=self.distribution,
                             identifier=fake.pystr(),
                             title="one_title",
                             present=False)
        Field.objects.create(distribution=self.distribution,
                             identifier=fake.pystr(),
                             title="other_title",
                             present=False)

        remove_duplicated_fields(self.distribution)

        self.assertEqual(self.distribution.field_set.count(), 2)
