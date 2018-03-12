# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import getpass
import requests

from crontab import CronTab
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
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
    catalog = models.TextField(default='{}')

    def __unicode__(self):
        return self.catalog_id

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            catalog_request = requests.get(self.catalog_url)
            if catalog_request.status_code != 200:
                return
            self.catalog = catalog_request.content
        except requests.exceptions.RequestException:
            self.catalog = open(self.catalog_url).read()

        super(Node, self).save(force_insert, force_update, using, update_fields)


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

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    @classmethod
    def info(cls, task, msg):
        with transaction.atomic():
            task = cls.objects.select_for_update().get(id=task.id)
            task.logs += msg + '\n'
            task.save()

    @classmethod
    def increment_indicator(cls, task, catalog_id, indicator_type):
        with transaction.atomic():
            task = cls.objects.select_for_update().get(id=task.id)
            indicator = task.indicator_set.get_or_create(
                type=indicator_type,
                node=Node.objects.get(catalog_id=catalog_id)
            )[0]
            indicator.value += 1
            indicator.save()


class Indicator(models.Model):

    CATALOG_NEW = 'catalog_new'
    CATALOG_UPDATED = 'catalog_updated'
    CATALOG_TOTAL = 'catalog_total'
    DATASET_NEW = 'dataset_new'
    DATASET_UPDATED = 'dataset_updated'
    DATASET_TOTAL = 'dataset_total'
    DISTRIBUTION_NEW = 'distribution_new'
    DISTRIBUTION_UPDATED = 'distribution_updated'
    DISTRIBUTION_TOTAL = 'distribution_total'
    FIELD_NEW = 'field_new'
    FIELD_UPDATED = 'field_updated'
    FIELD_TOTAL = 'field_total'

    FIELD_NOT_UPDATED = 'field_not_updated'
    FIELD_INDEXABLE = 'field_indexable'
    FIELD_NOT_INDEXABLE = 'field_not_indexable'

    TYPE_CHOICES = (
        (CATALOG_NEW, 'Catálogos nuevos'),
        (CATALOG_TOTAL, 'Catálogos totales'),
        (CATALOG_UPDATED, 'Catálogos actualizados'),
        (DATASET_NEW, 'Datasets nuevos'),
        (DATASET_TOTAL, 'Datasets totales'),
        (DATASET_UPDATED, 'Datasets actualizados'),
        (DISTRIBUTION_NEW, 'Distribuciones nuevas'),
        (DISTRIBUTION_TOTAL, 'Distribuciones totales'),
        (DISTRIBUTION_UPDATED, 'Distribuciones actualizadas'),
        (FIELD_NEW, 'Series nuevas'),
        (FIELD_TOTAL, 'Series totales'),
        (FIELD_UPDATED, 'Series actualizadas'),
        (FIELD_NOT_UPDATED, 'Series no actualizadas'),
        (FIELD_INDEXABLE, 'Series indexables'),
        (FIELD_NOT_INDEXABLE, 'Series no indexables'),
    )

    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    value = models.FloatField(default=0)
    node = models.ForeignKey(to=Node, on_delete=models.CASCADE)
    task = models.ForeignKey(to=ReadDataJsonTask, on_delete=models.CASCADE)
