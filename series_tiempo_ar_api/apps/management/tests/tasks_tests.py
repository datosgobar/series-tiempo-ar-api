#!coding=utf8
import os

from django.test import TestCase

from series_tiempo_ar_api.apps.api.models import Field
from series_tiempo_ar_api.apps.management.tasks import read_datajson
from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask, Node

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class ReadDataJsonTest(TestCase):

    def test_read(self):
        identifier = 'test_id'
        Node.objects.create(catalog_id=identifier,
                            catalog_url=os.path.join(dir_path, 'sample_data.json'),
                            indexable=True).save()
        task = ReadDataJsonTask()
        task.save()
        read_datajson(task, async=False)
        self.assertTrue(Field.objects.filter(distribution__dataset__catalog__identifier=identifier))
