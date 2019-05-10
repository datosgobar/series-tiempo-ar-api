from des.models import DynamicEmailConfiguration
from django.contrib.auth.models import User, Group
from django.test import TestCase

from django.core import mail

from django.conf import settings
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.management.models import IndexDataTask
from series_tiempo_ar_api.libs.indexing.report.node_admins import GlobalAdmins, NodeAdmins
from series_tiempo_ar_api.libs.indexing.report.report_generator import ReportGenerator
from series_tiempo_ar_api.libs.indexing.report.report_mail_sender import ReportMailSender


class ReportMailSenderTests(TestCase):

    def setUp(self) -> None:
        self.task = IndexDataTask.objects.create()
        user = User.objects.create(username="user", email="test@user.com", password="test_passwword")
        user.groups.add(Group.objects.get(name='read_datajson_recipients'))
        user.save()

    def test_mail_is_sent(self):
        ReportGenerator(self.task).generate()
        self.assertTrue(len(mail.outbox), 1)
