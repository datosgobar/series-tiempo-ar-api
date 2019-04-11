from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import send_mail


class ReportMailSender:

    def __init__(self, node):
        self.node = node

    def send(self):
        recipients = Group.objects.get(name=settings.READ_DATAJSON_RECIPIENT_GROUP).user_set.all()

        emails = [user.email for user in recipients]

        send_mail(subject='subject', message='test_mail', recipient_list=emails, from_email='test')
