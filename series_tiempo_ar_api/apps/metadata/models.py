#! coding: utf-8
import datetime
from typing import Sequence, List

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django_datajsonar.models import AbstractTask, Node
from solo.models import SingletonModel

from series_tiempo_ar_api.apps.management.models import TaskCron


class IndexMetadataTask(AbstractTask):
    pass


def validate_not_catalog_id(alias: str):
    ids = Node.objects.filter(catalog_id=alias)
    if ids:
        msg = f'Ya existe un catálogo con id {alias}, no puede ser usado como alias'
        raise ValidationError(msg)


class CatalogAlias(models.Model):
    class Meta:
        verbose_name_plural = "Catalog Aliases"

    nodes = models.ManyToManyField(Node, blank=True)
    alias = models.CharField(max_length=100, validators=[validate_not_catalog_id])

    def resolve(self) -> Sequence[str]:
        return self.nodes.values_list('catalog_id', flat=True)


class Synonym(models.Model):
    terms = models.TextField(
        help_text='Lista de términos similares, separados por coma, sin espacios ni mayúsculas.'
        ' Ejemplo "ipc,inflacion"', unique=True)


class MetadataConfig(SingletonModel):
    SCRIPT_PATH = settings.INDEX_METADATA_SCRIPT_PATH

    time = models.TimeField(help_text='Los segundos serán ignorados', default=datetime.time(hour=0, minute=0))

    def save(self, *args, **kwargs):
        super(MetadataConfig, self).save(*args, **kwargs)
        TaskCron.objects.update_or_create(task_script_path=self.SCRIPT_PATH,
                                          defaults={'time': self.time})
