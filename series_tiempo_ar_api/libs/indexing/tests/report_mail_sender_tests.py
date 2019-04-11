from des.models import DynamicEmailConfiguration
from django.contrib.auth.models import User, Group
from django.test import TestCase

from django.core import mail

from django.conf import settings
from django_datajsonar.models import Node

from series_tiempo_ar_api.libs.indexing.report.node_admins import GlobalAdmins, NodeAdmins
from series_tiempo_ar_api.libs.indexing.report.report_mail_sender import ReportMailSender


class ReportMailSenderTests(TestCase):

    def setUp(self):
        self.subject = 'test_subject'
        self.body = 'test_body'
        self.user = User.objects.create(username='test_user',
                                        password='test_password',
                                        email='test_email@mail.com')
        self.user.groups.add(Group.objects.get(name=settings.READ_DATAJSON_RECIPIENT_GROUP))
        self.admins = GlobalAdmins()

    def test_send_mail(self):
        ReportMailSender(admins=self.admins, subject=self.subject, body=self.body).send()

        self.assertEqual(len(mail.outbox), 1)

    def test_mail_sent_is_to_all_datajson_recipients_users(self):
        ReportMailSender(admins=self.admins, subject=self.subject, body=self.body).send()

        self.assertIn(self.user.email, mail.outbox[0].recipients())

    def test_if_no_recipients_mail_is_not_sent(self):
        self.user.groups.clear()
        ReportMailSender(admins=self.admins, subject=self.subject, body=self.body).send()
        self.assertEqual(len(mail.outbox), 0)

    def test_mail_send_with_attachment(self):
        sender = ReportMailSender(admins=self.admins, subject=self.subject, body=self.body)
        file_name, body = 'test.csv', 'body'
        sender.add_csv_attachment('test.csv', 'body')
        sender.send()

        attachment_file_name, attachment_body, _ = mail.outbox[0].attachments[0]

        self.assertEqual(file_name, attachment_file_name)
        self.assertEqual(body, attachment_body)

    def test_subject_and_body(self):
        ReportMailSender(admins=self.admins, subject=self.subject, body=self.body).send()
        self.assertEqual(mail.outbox[0].subject, self.subject)
        self.assertEqual(mail.outbox[0].body, self.body)

    def test_individual_node_report_it_sent_only_to_node_admins(self):
        node = Node.objects.create(indexable=True, catalog_id='catalog_id', catalog_url='http://catalog_url.com')
        email = 'other@test.email.com'
        node.admins.add(User.objects.create(username='other_user', password='other_password', email=email))
        ReportMailSender(admins=NodeAdmins(node), subject=self.subject, body=self.body).send()

        self.assertIn(email, mail.outbox[0].recipients())

    def test_from_email_is_read_from_des(self):
        email = 'new_from_email@test_mail.com'
        config = DynamicEmailConfiguration.get_solo()
        config.from_email = email
        config.save()
        ReportMailSender(admins=self.admins, subject=self.subject, body=self.body).send()
        self.assertEqual(mail.outbox[0].from_email, config.from_email)

    def test_add_plaintext_attachment(self):
        sender = ReportMailSender(admins=self.admins, subject=self.subject, body=self.body)
        file_name, body = 'plain.txt', 'body'
        sender.add_plaintext_attachment(file_name, body)
        sender.send()
        attachment_file_name, attachment_body, _ = mail.outbox[0].attachments[0]

        self.assertEqual(file_name, attachment_file_name)
        self.assertEqual(body, attachment_body)
