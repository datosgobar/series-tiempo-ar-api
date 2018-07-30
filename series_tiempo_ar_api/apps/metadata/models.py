#! coding: utf-8
from typing import Sequence
from django.core.exceptions import ValidationError
from django.db import models
from django_datajsonar.models import AbstractTask, Node


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
