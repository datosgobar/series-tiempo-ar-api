#! coding: utf-8
from typing import Sequence, List
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


class Synonym(models.Model):
    terms = models.TextField(
        help_text='Lista de términos similares, separados por coma, sin espacios ni mayúsculas.'
        ' Ejemplo "ipc,inflacion"', unique=True)

    @classmethod
    def get_synonyms_list(cls) -> List[str]:
        synonyms = cls.objects.all()

        return [s.terms for s in synonyms]
