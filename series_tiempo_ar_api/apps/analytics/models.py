# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Query(models.Model):
    """Registro de queries exitosas, guardadas con el propósito de analytics"""
    ids = models.TextField()
    args = models.TextField()
    timestamp = models.DateTimeField()
    ip_address = models.CharField(max_length=200, null=True)
    params = models.TextField()

    def __unicode__(self):
        return u'Query at %s: %s' % (self.timestamp, self.ids)
