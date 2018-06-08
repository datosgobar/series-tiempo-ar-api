# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from django.db import models
from django.core.exceptions import ValidationError
from solo.models import SingletonModel


class Query(models.Model):
    """Registro de queries exitosas, guardadas con el propósito de analytics"""
    ids = models.TextField()
    args = models.TextField()
    timestamp = models.DateTimeField()
    ip_address = models.CharField(max_length=200, null=True)
    params = models.TextField()

    def __unicode__(self):
        return u'Query at %s: %s' % (self.timestamp, self.ids)


class ImportConfig(SingletonModel):
    endpoint = models.URLField()
    token = models.CharField(max_length=64)
    kong_api_id = models.CharField(max_length=64)

    def clean(self):
        status_code = requests.head(
            self.endpoint,
            headers={'Authorization': 'Token {}'.format(self.token)}
        ).status_code

        if status_code != 200:
            raise ValidationError('URL / Token inválido')

    def get_results(self, from_date=None, to_date=None, limit=1000, offset=0):
        return requests.get(
            self.endpoint,
            headers={'Authorization': 'Token {}'.format(self.token)},
            params={'from_date': from_date,
                    'to_date': to_date,
                    'limit': limit,
                    'offset': offset,
                    'kong_api_id': self.kong_api_id}
        ).json()
