#!coding=utf8
from __future__ import unicode_literals

import json

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.utils import timezone
from . import strings


class ReportGenerator(object):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, task):
        self.task = task

    def generate(self):
        self.task.finished = timezone.now()
        self.task.status = self.task.FINISHED
        self.task.save()
        self.generate_email()

    def generate_email(self):
        start_time = self._format_date(self.task.created)
        finish_time = self._format_date(self.task.finished)
        msg = "Horario de finalización: {}\n".format(finish_time)

        msg += self.format_message('catalogs', 'Catálogos')
        msg += self.format_message('datasets', 'Datasets')
        msg += self.format_message('distributions', 'Distribuciones')
        msg += self.format_message('fields', 'Series')

        recipients = Group.objects.get(name=settings.READ_DATAJSON_RECIPIENT_GROUP)
        emails = [user.email for user in recipients.user_set.all()]
        subject = u'[{}] API Series de Tiempo: {}'.format(settings.ENV_TYPE, start_time)

        sent = send_mail(subject, msg, settings.EMAIL_HOST_USER, emails)
        if emails and not sent:
            raise ValueError

    def format_message(self, dict_key, full_name):
        template = strings.INDEXING_REPORT_TEMPLATE
        stats = json.loads(self.task.stats)
        total_stats = {}
        for catalog in stats:
            for key in stats[catalog]:
                total_stats[key] = total_stats.get(key, 0) + stats[catalog][key]

        total_catalogs = total_stats.get('total_' + dict_key, 0)
        new_catalogs = total_stats.get(dict_key, 0)
        updated_catalogs = total_catalogs - new_catalogs
        msg = template.format(name=full_name,
                              new=new_catalogs,
                              updated=updated_catalogs,
                              total=total_catalogs)
        return msg

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)
