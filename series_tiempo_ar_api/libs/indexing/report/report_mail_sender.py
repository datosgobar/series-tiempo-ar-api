from django.core.mail import send_mail


class ReportMailSender:

    def __init__(self, node):
        self.node = node

    def send(self):
        send_mail(subject='subject', message='test_mail', recipient_list=['test@email.com'], from_email='test')
