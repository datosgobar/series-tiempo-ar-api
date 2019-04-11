from des.models import DynamicEmailConfiguration
from django.core.mail import EmailMultiAlternatives


class ReportMailSender:

    def __init__(self, admins, subject, body):
        self.admins = admins
        self.subject = subject
        self.body = body
        self.attachments = []

    def send(self):
        emails = self.admins.get_emails()

        config = DynamicEmailConfiguration.get_solo()
        mail = EmailMultiAlternatives(self.subject, self.body, from_email=config.from_email, to=emails)

        for file_name, body in self.attachments:
            mail.attach(file_name, body, 'text/csv')

        mail.send()

    def add_csv_attachment(self, file_name, body):
        self.attachments.append((file_name, body))
