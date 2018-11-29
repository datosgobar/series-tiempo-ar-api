# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import requests
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from solo.models import SingletonModel

from series_tiempo_ar_api.apps.management.models import TaskCron


class Query(models.Model):
    """Registro de queries exitosas, guardadas con el propósito de analytics"""
    ids = models.TextField()
    args = models.TextField()
    timestamp = models.DateTimeField()
    ip_address = models.CharField(max_length=200, null=True)
    params = models.TextField()

    api_mgmt_id = models.IntegerField(blank=True, null=True, unique=True)

    uri = models.TextField(default='')
    status_code = models.IntegerField(default=0)
    user_agent = models.TextField(default='')
    request_time = models.DecimalField(max_digits=30, decimal_places=25, default=0)

    def __unicode__(self):
        return u'Query at %s: %s' % (self.timestamp, self.ids)


class ImportConfig(SingletonModel):
    SCRIPT_PATH = settings.IMPORT_ANALYTICS_SCRIPT_PATH

    endpoint = models.URLField()
    token = models.CharField(max_length=64)
    kong_api_id = models.CharField(max_length=64)
    time = models.TimeField(help_text='Los segundos serán ignorados', default=datetime.time(hour=0, minute=0))

    last_cursor = models.CharField(max_length=64, blank=True)

    def clean(self):
        status_code = requests.head(
            self.endpoint,
            headers={'Authorization': 'Token {}'.format(self.token)}
        ).status_code

        if status_code != 200:
            raise ValidationError('URL / Token inválido')

    def get_results(self, from_date=None, to_date=None, limit=1000, offset=0):
        """Wrapper sobre requests para pegarle al endpoint configurado"""
        return requests.get(
            self.endpoint,
            headers=self.get_authorization_header(),
            params={'from_date': from_date,
                    'to_date': to_date,
                    'limit': limit,
                    'offset': offset,
                    'kong_api_id': self.kong_api_id}
        ).json()

    def get_authorization_header(self):
        """Devuelve el header de auth formateado para usar en la libreria de requests"""
        return {'Authorization': 'Token {}'.format(self.token)}

    def save(self, *args, **kwargs):
        super(ImportConfig, self).save(*args, **kwargs)
        TaskCron.objects.update_or_create(task_script_path=self.SCRIPT_PATH,
                                          defaults={'time': self.time})


class AnalyticsImportTask(models.Model):

    RUNNING = 'running'
    FINISHED = 'finished'

    STATUS_CHOICES = (
        (RUNNING, "Corriendo"),
        (FINISHED, "Finalizada"),
    )

    status = models.CharField(max_length=64, choices=STATUS_CHOICES)
    logs = models.TextField(blank=True)
    timestamp = models.DateTimeField()

    def __str__(self):
        return "Analytics import task at {}".format(self.timestamp)

    def write_logs(self, text):
        if not self.logs:
            self.logs = ''

        self.logs += text + '\n'
        self.save()
