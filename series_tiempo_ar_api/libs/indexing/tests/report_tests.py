import os

from django.contrib.auth.models import User, Group
from django.test import TestCase

from django.core import mail
from django_datajsonar.models import Distribution

from series_tiempo_ar_api.apps.management.models import IndexDataTask
from series_tiempo_ar_api.libs.indexing.report.report_generator import ReportGenerator
from series_tiempo_ar_api.libs.utils.utils import test_read_datajson

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


class ReportMailSenderTests(TestCase):

    def setUp(self) -> None:
        self.task = IndexDataTask.objects.create()
        user = User.objects.create(username="user", email="test@user.com", password="test_passwword")
        user.groups.add(Group.objects.get(name='read_datajson_recipients'))
        user.save()

    def test_mail_is_sent(self):
        ReportGenerator(self.task).generate()
        self.assertTrue(len(mail.outbox), 1)

    def test_mail_has_distribution_error_in_body(self):
        test_read_datajson('test_catalog', os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        Distribution.objects.update(error_msg="My error message")
        ReportGenerator(self.task).generate()
        self.assertIn("My error message", mail.outbox[0].body)
