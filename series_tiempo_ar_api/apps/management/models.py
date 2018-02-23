# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import getpass

from crontab import CronTab
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from . import strings


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


class IndexingTaskCron(models.Model):
    cron_client = CronTab(user=getpass.getuser())

    time = models.TimeField(help_text='Los segundos serán ignorados')
    enabled = models.BooleanField(default=True)
    weekdays_only = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(IndexingTaskCron, self).__init__(*args, **kwargs)

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
        command = settings.READ_DATAJSON_SHELL_CMD
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
    catalogs = models.ManyToManyField(to=Node, blank=True)

    stats = models.TextField(default='{}')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:  # first time only
            self.created = timezone.now()
            self.status = self.RUNNING

        super(ReadDataJsonTask, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return "Task at %s" % self._format_date(self.created)

    def generate_email(self):
        start_time = self._format_date(self.created)
        finish_time = self._format_date(self.finished)
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
        stats = json.loads(self.stats)
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
