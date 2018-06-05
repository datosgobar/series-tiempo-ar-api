#!coding=utf8

from django.db import models
from django_datajsonar.models import AbstractTask
from . import constants


class CSVDumpTask(AbstractTask):
    pass


class DumpFile(models.Model):

    file = models.FileField(upload_to='dump')

    FILE_CHOICES = (
        (constants.FULL_CSV, 'Valores y metadatos (CSV)'),
        (constants.VALUES_CSV, 'Valores (CSV)'),
        (constants.METADATA_CSV, 'Metadatos enriquecidos de las series (CSV)'),
        (constants.SOURCES_CSV, 'Fuentes (CSV)'),
        (constants.FULL_CSV_ZIPPED, 'Valores y metadatos (CSV, zipped)'),
    )

    file_name = models.CharField(max_length=64, choices=FILE_CHOICES)
    task = models.ForeignKey(CSVDumpTask, on_delete=models.CASCADE)
