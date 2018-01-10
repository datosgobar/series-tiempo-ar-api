# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import getpass

from crontab import CronTab
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class BaseRegisterFile(models.Model):
    """Base de los archivos de registro de datasets y de nodos.
    Contiene atributos de estado del archivo y fechas de creado / modificado
    """
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

    STATE_CHOICES = (
        (UPLOADED, "Cargado"),
        (PROCESSING, "Procesando"),
        (PROCESSED, "Procesado"),
        (FAILED, "Error"),
    )

    created = models.DateTimeField()
    modified = models.DateTimeField(null=True)
    indexing_file = models.FileField(upload_to='register_files/')
    uploader = models.ForeignKey(User)
    state = models.CharField(max_length=20, choices=STATE_CHOICES)
    logs = models.TextField(default=u'-')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:  # first time only
            self.created = timezone.now()
            self.state = self.UPLOADED

        super(BaseRegisterFile, self).save(force_insert, force_update, using, update_fields)


class DatasetIndexingFile(BaseRegisterFile):
    def __unicode__(self):
        return "Indexing file: {}".format(self.created)


class Node(models.Model):

    catalog_id = models.CharField(max_length=100, unique=True)
    catalog_url = models.URLField()
    indexable = models.BooleanField()

    def __unicode__(self):
        return self.catalog_id


class NodeRegisterFile(BaseRegisterFile):
    def __unicode__(self):
        return "Node register file: {}".format(self.created)


class IndexingTask(models.Model):

    time = models.TimeField(help_text='Los segundos serán ignorados')
    enabled = models.BooleanField(default=True)
    weekdays_only = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(IndexingTask, self).save(force_insert, force_update, using, update_fields)
        self.update_crontab()

    def delete(self, using=None, keep_parents=False):
        super(IndexingTask, self).delete(using, keep_parents)
        self.update_crontab()

    def __unicode__(self):
        return u'Indexing task at %s' % self.time

    @staticmethod
    def update_crontab():
        python_exec = sys.executable
        cwd = os.getcwd()

        command = '%s %s/manage.py read_datajson' % (python_exec, cwd)
        cron = CronTab(user=getpass.getuser())

        job_id = "API series tiempo: indexing de datos"
        for job in cron.find_comment(job_id):
            job.delete()

        tasks = IndexingTask.objects.filter(enabled=True)
        for task in tasks:
            job = cron.new(command=command, comment=job_id)

            job.minute.on(task.time.minute)
            job.hour.on(task.time.hour)
            if task.weekdays_only:
                job.dow.during('MON', 'FRI')

        cron.write()
