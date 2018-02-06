#!coding=utf8
import os

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core import mail
from django.core.management import call_command
from django.test import TestCase

from series_tiempo_ar_api.apps.api.models import Field
from series_tiempo_ar_api.apps.management.tasks import read_datajson
from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask, Node

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class ReadDataJsonTest(TestCase):

    def setUp(self):
        self.user = User(username='test', password='test', email='test@test.com', is_staff=True)
        self.user.save()

    def test_read(self):
        identifier = 'test_id'
        Node(catalog_id=identifier,
             catalog_url=os.path.join(dir_path, 'sample_data.json'),
             indexable=True).save()
        task = ReadDataJsonTask()
        task.save()
        read_datajson(task, async=False, whitelist=True)
        self.assertTrue(Field.objects.filter(distribution__dataset__catalog__identifier=identifier))

    def test_read_invalid(self):
        identifier = 'test_id'
        # noinspection PyUnresolvedReferences
        Node.objects.create(catalog_id=identifier,
                            catalog_url=os.path.join(dir_path, 'missing_data.json'),
                            indexable=True).save()
        task = ReadDataJsonTask()
        task.save()
        read_datajson(task, async=False, whitelist=True)

        # Esperado: logs con errores
        self.assertTrue(task.logs)

    def test_read_datajson_command(self):
        identifier = 'test_id'
        Node(catalog_id=identifier,
             catalog_url=os.path.join(dir_path, 'sample_data.json'),
             indexable=True).save()
        # Esperado: mismo comportamiento que llamando la función read_datajson
        call_command('read_datajson', whitelist=True)
        self.assertTrue(Field.objects.filter(distribution__dataset__catalog__identifier=identifier))

    def test_read_datajson_while_indexing(self):
        identifier = 'test_id'
        Node(catalog_id=identifier,
             catalog_url=os.path.join(dir_path, 'sample_data.json'),
             indexable=True).save()

        ReadDataJsonTask(status=ReadDataJsonTask.INDEXING).save()

        # Esperado: no se crea una segunda tarea
        call_command('read_datajson')
        self.assertEqual(ReadDataJsonTask.objects.all().count(), 1)

    def test_report_sent(self):
        identifier = 'test_id'
        Node(catalog_id=identifier,
             catalog_url=os.path.join(dir_path, 'sample_data.json'),
             indexable=True).save()

        group = Group.objects.get(name=settings.READ_DATAJSON_RECIPIENT_GROUP)
        self.user.groups.add(group)
        self.user.save()
        call_command('read_datajson', no_async=True)

        self.assertEqual(len(mail.outbox), 1)
