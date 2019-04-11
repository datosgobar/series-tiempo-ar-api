from django.contrib.auth.models import User, Group
from django.test import TestCase

from django.core import mail

from django.conf import settings
from series_tiempo_ar_api.libs.indexing.report.report_mail_sender import ReportMailSender


class ReportMailSenderTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user',
                                        password='test_password',
                                        email='test_email@mail.com')
        self.user.groups.add(Group.objects.get(name=settings.READ_DATAJSON_RECIPIENT_GROUP))

    def test_send_mail(self):
        ReportMailSender(node=None).send()

        self.assertEqual(len(mail.outbox), 1)

    def test_mail_sent_is_to_all_datajson_recipients_users(self):
        ReportMailSender(node=None).send()

        self.assertIn(self.user.email, mail.outbox[0].recipients())

    def test_if_no_recipients_mail_is_not_sent(self):
        self.user.groups.clear()
        ReportMailSender(node=None).send()
        self.assertEqual(len(mail.outbox), 0)

    def test_mail_send_with_attachment(self):
        sender = ReportMailSender(node=None)
        file_name, body = 'test.csv', 'body'
        sender.add_csv_attachment('test.csv', 'body')
        sender.send()

        attachment_file_name, attachment_body, _ = mail.outbox[0].attachments[0]

        self.assertEqual(file_name, attachment_file_name)
        self.assertEqual(body, attachment_body)
