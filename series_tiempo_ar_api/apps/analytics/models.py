# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import requests
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from solo.models import SingletonModel
from django_datajsonar.models import AbstractTask


class Query(models.Model):
    """Registro de queries exitosas, guardadas con el propósito de analytics"""

    class Meta:
        verbose_name_plural = "Tabla consultas"

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
    class Meta:
        verbose_name = "Configuración de importación de analytics"

    SCRIPT_PATH = settings.IMPORT_ANALYTICS_SCRIPT_PATH

    endpoint = models.URLField()
    token = models.CharField(max_length=64)
    kong_api_id = models.CharField(max_length=64)

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


class AnalyticsImportTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Corridas de importación de analytics"
        verbose_name = "Corrida de importación de analytics"


class HitsIndicator(models.Model):

    class Meta:
        verbose_name = 'Consultas por día de serie'
        verbose_name_plural = 'Consultas por día de series'
        unique_together = ('serie_id', 'date', )

    serie_id = models.CharField(max_length=64)
    date = models.DateField()
    hits = models.IntegerField()
