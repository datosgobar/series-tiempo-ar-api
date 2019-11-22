import html
import os

import mock
from django.contrib.auth.models import User, Group
from django.test import TestCase

from django.core import mail
from django_datajsonar.models import Distribution, Node, Catalog

from series_tiempo_ar_api.apps.management.models import IndexDataTask
from series_tiempo_ar_api.libs.indexing.report.report_generator import ReportGenerator
from series_tiempo_ar_api.libs.utils.utils import index_catalog

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


@mock.patch('series_tiempo_ar_api.libs.indexing.tasks.DistributionIndexer')
class ReportMailSenderTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Catalog.objects.all().delete()

    def setUp(self) -> None:
        self.mock_index = 'test_index'
        self.task = IndexDataTask.objects.create()
        user = User.objects.create(username="user", email="test@user.com", password="test_passwword")
        user.groups.add(Group.objects.get(name='read_datajson_recipients'))
        user.save()

    def test_mail_is_sent(self, *_):
        ReportGenerator(self.task).generate()
        self.assertTrue(len(mail.outbox), 1)

    def test_mail_has_distribution_error_in_body(self, *_):
        self.index_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        Distribution.objects.update(error=True, error_msg="My error message")
        ReportGenerator(self.task).generate()
        self.assertIn("My error message", mail.outbox[0].body)

    def test_report_of_some_errored_distributions_some_ok(self, *_):
        self.index_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'one_distribution_ok_one_error.json'))
        ReportGenerator(self.task).generate()
        error_msg = Distribution.objects.filter(error=True).first().error_msg
        self.assertIn(error_msg, html.unescape(mail.outbox[0].body))

    def test_report_errors_in_one_catalog_ok_in_other(self, *_):
        self.index_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'one_distribution_ok_one_error.json'))
        self.index_catalog('other_catalog', os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        error_msg = Distribution.objects.filter(error=True).first().error_msg
        ReportGenerator(self.task).generate()
        self.assertIn(error_msg, mail.outbox[0].body)
        self.assertNotIn(Distribution.objects.filter(error=False).first().identifier, mail.outbox[0].body)

    def test_single_node_report_is_sent(self, *_):
        self.index_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        Node.objects.get(catalog_id='test_catalog').admins.add(User.objects.first())
        ReportGenerator(self.task).generate()

        self.assertTrue(len(mail.outbox), 2)

    def test_single_node_report_has_errors_only_from_its_own_catalog(self, *_):
        self.index_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'one_distribution_ok_one_error.json'))
        self.index_catalog('other_catalog', os.path.join(SAMPLES_DIR, 'broken_catalog.json'))
        Node.objects.get(catalog_id='test_catalog').admins.add(User.objects.first())

        error_id = Distribution.objects.filter(dataset__catalog__identifier='test_catalog',
                                               error=True).first().identifier
        other_id = Distribution.objects.filter(
            dataset__catalog__identifier='other_catalog',
            error=True).first().identifier
        ReportGenerator(self.task).generate()
        self.assertIn(error_id, mail.outbox[1].body)
        self.assertNotIn(other_id, mail.outbox[1].body)

    def test_errors_from_multiple_catalogs_sorted_by_catalog_id(self, *_):
        self.index_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'one_distribution_ok_one_error.json'))
        self.index_catalog('other_catalog', os.path.join(SAMPLES_DIR, 'broken_catalog.json'))
        ReportGenerator(self.task).generate()
        error_id = Distribution.objects.filter(dataset__catalog__identifier='test_catalog',
                                               error=True).first().identifier
        other_id = Distribution.objects.filter(
            dataset__catalog__identifier='other_catalog',
            error=True).first().identifier

        body = mail.outbox[0].body
        self.assertGreater(body.index(error_id), body.index(other_id))

    def test_errors_in_same_distribution_sorted_by_distribution_id(self, *_):
        self.index_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'broken_catalog.json'))
        ReportGenerator(self.task).generate()
        sorted_error_ids = sorted(Distribution.objects.filter(
            dataset__catalog__identifier='test_catalog',
            error=True).values_list('identifier', flat=True))

        first_error_id = sorted_error_ids[0]
        second_error_id = sorted_error_ids[1]
        body = mail.outbox[0].body
        self.assertGreater(body.index(second_error_id), body.index(first_error_id))

    def test_error_logs_attachment(self, *_):
        self.index_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'broken_catalog.json'))
        error_id = Distribution.objects.filter(dataset__catalog__identifier='test_catalog',
                                               error=True).first().identifier
        self.task.logs = f"Error en distribución {error_id}"
        self.task.save()
        ReportGenerator(self.task).generate()
        log_body = mail.outbox[0].attachments[-1][1]
        self.assertIn(error_id, log_body)

    def test_error_logs_for_single_node(self, *_):
        self.index_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'one_distribution_ok_one_error.json'))
        Node.objects.get(catalog_id='test_catalog').admins.add(User.objects.first())
        self.index_catalog('other_catalog', os.path.join(SAMPLES_DIR, 'broken_catalog.json'))
        ReportGenerator(self.task).generate()
        error_id = Distribution.objects.filter(dataset__catalog__identifier='test_catalog',
                                               error=True).first().identifier
        log_body = mail.outbox[1].attachments[-1][1]
        self.assertIn(error_id, log_body)

    def test_error_logs_for_single_node_does_not_have_other_catalog_errors(self, *_):
        self.index_catalog('test_catalog', os.path.join(SAMPLES_DIR, 'one_distribution_ok_one_error.json'))
        Node.objects.get(catalog_id='test_catalog').admins.add(User.objects.first())
        self.index_catalog('other_catalog', os.path.join(SAMPLES_DIR, 'broken_catalog.json'))
        ReportGenerator(self.task).generate()
        other_id = Distribution.objects.filter(
            dataset__catalog__identifier='other_catalog',
            error=True).first().identifier
        log_body = mail.outbox[1].attachments[-1][1]
        self.assertNotIn(other_id, log_body)

    def index_catalog(self, catalog_id, catalog_path):
        index_catalog(catalog_id, catalog_path, self.mock_index)
