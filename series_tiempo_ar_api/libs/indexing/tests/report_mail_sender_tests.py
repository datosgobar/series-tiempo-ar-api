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
