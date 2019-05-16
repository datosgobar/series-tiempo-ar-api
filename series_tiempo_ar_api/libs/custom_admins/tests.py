import os

import mock
from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import User
from django.core import urlresolvers
from django.test import TestCase
from django_datajsonar.models import Node, ReadDataJsonTask, Field, Distribution

from django_datajsonar.indexing.catalog_reader import index_catalog

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


@mock.patch('series_tiempo_ar_api.libs.custom_admins.admin.delete_metadata')
class DeleteMetadataTests(TestCase):
    distribution_change = urlresolvers.reverse('admin:django_datajsonar_distribution_changelist')
    field_change = urlresolvers.reverse('admin:django_datajsonar_field_changelist')

    def setUp(self):
        self.catalog_id = "one"
        node = Node.objects.create(catalog_url=os.path.join(SAMPLES_DIR, 'single_distribution.json'),
                                   catalog_id=self.catalog_id,
                                   indexable=True)
        index_catalog(node, ReadDataJsonTask.objects.create(), whitelist=True)
        user = User.objects.create(username='a', password='b', is_staff=True, is_superuser=True)
        self.client.force_login(user)

    def test_delete_fields(self, fake_delete):
        fields = Field.objects.all()
        self.client.post(self.field_change, {'action': 'delete_model',
                                             ACTION_CHECKBOX_NAME: [str(f.pk) for f in fields]},
                         follow=True)

        self.assertEqual(set(fake_delete.call_args[0][0]), set(fields))

    def test_delete_distribution(self, fake_delete):
        distribution: Distribution = Distribution.objects.filter(dataset__catalog__identifier=self.catalog_id).first()
        fields = set(distribution.field_set.all())
        self.client.post(self.distribution_change,
                         {'action': 'delete_model',
                          ACTION_CHECKBOX_NAME: [str(distribution.pk)]},
                         follow=True)
        self.assertEqual(set(fake_delete.call_args[0][0]), set(fields))
