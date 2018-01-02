# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class Query(models.Model):
    """Registro de queries exitosas, guardadas con el propósito de analytics"""
    ids = models.CharField(max_length=2000)
    args = models.CharField(max_length=2000)
    timestamp = models.DateTimeField()
    ip_address = models.CharField(max_length=200, null=True)
    params = models.TextField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.timestamp = timezone.now()
        super(Query, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return u'Query at %s: %s' % (self.timestamp, self.ids)
