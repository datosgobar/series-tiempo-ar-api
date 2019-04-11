from des.models import DynamicEmailConfiguration
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives


class ReportMailSender:

    def __init__(self, node):
        self.node = node
        self.attachments = []

    def send(self):
        recipients = Group.objects.get(name=settings.READ_DATAJSON_RECIPIENT_GROUP).user_set.all()

        emails = [user.email for user in recipients]

        config = DynamicEmailConfiguration.get_solo()
        mail = EmailMultiAlternatives('test', 'test', from_email=config.from_email, to=emails)

        for file_name, body in self.attachments:
            mail.attach(file_name, body, 'text/csv')

        mail.send()

    def add_csv_attachment(self, file_name, body):
        self.attachments.append((file_name, body))
