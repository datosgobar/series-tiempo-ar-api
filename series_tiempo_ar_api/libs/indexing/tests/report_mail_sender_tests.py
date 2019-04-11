from django.test import TestCase

from django.core import mail

from series_tiempo_ar_api.libs.indexing.report.report_mail_sender import ReportMailSender


class ReportMailSenderTests(TestCase):

    def test_send_mail(self):
        ReportMailSender(node=None).send()

        self.assertEqual(len(mail.outbox), 1)
