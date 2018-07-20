# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import getpass

from django_datajsonar import models as djar_models
from crontab import CronTab
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from . import strings
from .indicator_names import IndicatorNamesMixin


class IndexingTaskCron(models.Model):
    cron_client = CronTab(user=getpass.getuser())

    time = models.TimeField(help_text='Los segundos serán ignorados')
    enabled = models.BooleanField(default=True)
    weekdays_only = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(IndexingTaskCron, self).save(force_insert, force_update, using, update_fields)
        self.update_crontab()

    def delete(self, using=None, keep_parents=False):
        super(IndexingTaskCron, self).delete(using, keep_parents)
        self.update_crontab()

    def __unicode__(self):
        return u'Indexing task at %s' % self.time

    @classmethod
    def update_crontab(cls):
        """Limpia la crontab y la regenera a partir de los modelos de IndexingTaskCron guardados"""
        command = settings.READ_DATAJSON_SHELL_CMD or 'true'
        cron = cls.cron_client

        job_id = strings.CRONTAB_COMMENT
        for job in cron.find_comment(job_id):
            job.delete()

        tasks = IndexingTaskCron.objects.filter(enabled=True)
        for task in tasks:
            job = cron.new(command=command, comment=job_id)

            job.minute.on(task.time.minute)
            job.hour.on(task.time.hour)
            if task.weekdays_only:
                job.dow.during('MON', 'FRI')

        cron.write()

class ReadDataJsonTask(models.Model):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    RUNNING = "RUNNING"
    INDEXING = "INDEXING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"

    STATUS_CHOICES = (
        (RUNNING, "Procesando catálogos"),
        (INDEXING, "Indexando series"),
        (FINISHED, "Finalizada"),
        (ERROR, "Error"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created = models.DateTimeField()
    finished = models.DateTimeField(null=True)
    logs = models.TextField(default='-')

    stats = models.TextField(default='{}')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:  # first time only
            self.created = timezone.now()
            self.status = self.RUNNING

        super(ReadDataJsonTask, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return "Task at %s" % self._format_date(self.created)

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    @classmethod
    def info(cls, task, msg):
        with transaction.atomic():
            task = cls.objects.select_for_update().get(id=task.id)
            task.logs += msg + '\n'
            task.save()


class Indicator(models.Model, IndicatorNamesMixin):

    class Meta:
        unique_together = ('type', 'node', 'task',)

    type = models.CharField(max_length=100, choices=IndicatorNamesMixin.TYPE_CHOICES)
    value = models.FloatField(default=0)
    node = models.ForeignKey(to=djar_models.Node, on_delete=models.CASCADE)
    task = models.ForeignKey(to=ReadDataJsonTask, on_delete=models.CASCADE)


class NodeAdmins(models.Model):
    class Meta:
        verbose_name_plural = 'Node admins'

    node = models.OneToOneField(to=djar_models.Node)
    admins = models.ManyToManyField(to=User)

    def __str__(self):
        return "Admins de {}".format(self.node.catalog_id)
