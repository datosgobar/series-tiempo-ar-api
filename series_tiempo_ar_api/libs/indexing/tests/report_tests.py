import os

from django.contrib.auth.models import User, Group
from django.test import TestCase

from django.core import mail
from django_datajsonar.models import Distribution, Node

from series_tiempo_ar_api.apps.management.models import IndexDataTask
from series_tiempo_ar_api.libs.indexing.report.report_generator import ReportGenerator
from series_tiempo_ar_api.libs.utils.utils import parse_catalog

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
        parse_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        Distribution.objects.update(error=True, error_msg="My error message")
        ReportGenerator(self.task).generate()
        self.assertIn("My error message", mail.outbox[0].body)

    def test_report_of_some_errored_distributions_some_ok(self):
        parse_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'one_distribution_ok_one_error.json'))
        ReportGenerator(self.task).generate()
        error_msg = Distribution.objects.filter(error=True).first().error_msg
        self.assertIn(error_msg, mail.outbox[0].body)

    def test_report_errors_in_one_catalog_ok_in_other(self):
        parse_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'one_distribution_ok_one_error.json'))
        parse_catalog('other_catalog', os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        error_msg = Distribution.objects.filter(error=True).first().error_msg
        ReportGenerator(self.task).generate()
        self.assertIn(error_msg, mail.outbox[0].body)
        self.assertNotIn(Distribution.objects.filter(error=False).first().identifier, mail.outbox[0].body)

    def test_single_node_report_is_sent(self):
        parse_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        Node.objects.get(catalog_id='test_catalog').admins.add(User.objects.first())
        ReportGenerator(self.task).generate()

        self.assertTrue(len(mail.outbox), 2)
