# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db import models
from solo.models import SingletonModel
from django_datajsonar import models as djar_models

from .indicator_names import IndicatorNamesMixin


class IndexDataTask(djar_models.AbstractTask):
    class Meta:
        verbose_name = "Corrida de indexación de datos"
        verbose_name_plural = "Corridas de indexación de datos"

    UPDATED_ONLY = 'updated'
    ALL = 'all'
    INDEXING_CHOICES = (
        (UPDATED_ONLY, 'Sólo actualizados'),
        (ALL, 'Todos (forzar indexación)')
    )

    indexing_mode = models.CharField(choices=INDEXING_CHOICES, default=UPDATED_ONLY, max_length=200)


class Indicator(models.Model, IndicatorNamesMixin):

    class Meta:
        unique_together = ('type', 'node', 'task',)

    type = models.CharField(max_length=100, choices=IndicatorNamesMixin.TYPE_CHOICES)
    value = models.FloatField(default=0)
    node = models.ForeignKey(to=djar_models.Node, on_delete=models.CASCADE)
    task = models.ForeignKey(to=IndexDataTask, on_delete=models.CASCADE)


class IntegrationTestTask(djar_models.AbstractTask):
    class Meta:
        verbose_name = "Corrida de test de integración"
        verbose_name_plural = "Corridas de test de integración"

    def log(self, string: str):
        self.__class__.info(self, string)


class IntegrationTestConfig(SingletonModel):
    class Meta:
        verbose_name = "Configuración del test de integración"

    SCRIPT_PATH = settings.INTEGRATION_TEST_SCRIPT_PATH

    recipients = models.ManyToManyField(User, blank=True, verbose_name="Destinatarios")
    api_endpoint = models.URLField(help_text="URL completa de la API de series a usar como referencia "
                                             "en los mail de error")
    timeout = models.IntegerField(default=1000)


class APIIndexingConfig(SingletonModel):
    class Meta:
        verbose_name = 'Configuración de rutina de indexación'

    indexing_timeout = models.IntegerField(default=1000)
