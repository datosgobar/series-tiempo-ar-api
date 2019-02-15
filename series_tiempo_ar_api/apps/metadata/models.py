#! coding: utf-8
import datetime
from typing import Sequence

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.postgres.fields import JSONField
from django_datajsonar.models import AbstractTask, Node
from solo.models import SingletonModel


class IndexMetadataTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Corridas de indexación de metadatos"
        verbose_name = "Corrida de indexación de metadatos"


def validate_not_catalog_id(alias: str):
    ids = Node.objects.filter(catalog_id=alias)
    if ids:
        msg = f'Ya existe un catálogo con id {alias}, no puede ser usado como alias'
        raise ValidationError(msg)


class CatalogAlias(models.Model):
    class Meta:
        verbose_name_plural = "Catalogs Aliases"
        verbose_name = "Catalogs alias"

    nodes = models.ManyToManyField(Node, blank=True)
    alias = models.CharField(max_length=100, validators=[validate_not_catalog_id])

    def resolve(self) -> Sequence[str]:
        return self.nodes.values_list('catalog_id', flat=True)


class Synonym(models.Model):
    class Meta:
        verbose_name_plural = "Sinónimos de búsqueda"
        verbose_name = "Sinónimo de búsqueda"

    terms = models.TextField(
        help_text='Lista de términos similares, separados por coma, sin espacios ni mayúsculas.'
        ' Ejemplo "ipc,inflacion"', unique=True)


class MetadataConfig(SingletonModel):
    class Meta:
        verbose_name = "Configuración de búsqueda de series por metadatos"

    SCRIPT_PATH = settings.INDEX_METADATA_SCRIPT_PATH

    query_config = JSONField(default={'dataset_description': {'boost': 1},
                                      'dataset_source': {'boost': 1},
                                      'dataset_title': {'boost': 1},
                                      'description': {'boost': 1.5}})
