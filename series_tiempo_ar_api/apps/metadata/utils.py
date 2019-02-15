#! coding: utf-8
import random
from typing import Sequence, List

from django.utils import timezone
from series_tiempo_ar_api.apps.metadata.models import CatalogAlias


def resolve_catalog_id_aliases(aliases: Sequence[str]) -> List[str]:
    """
    Expande cada término en la lista de aliases en los catalog_id que representa.
    Si algún alias no existe, se interpreta como un catalog_id directamente y
    se devuelve como está.
    """
    catalog_ids = []
    for catalog_id in aliases:
        try:
            catalog_ids.extend(CatalogAlias.objects.get(alias=catalog_id).resolve())
        except CatalogAlias.DoesNotExist:
            catalog_ids.append(catalog_id)

    return catalog_ids


def get_random_index_name():
    return f"metadata-{random.randrange(1000000)}-{int(timezone.now().timestamp())}"
