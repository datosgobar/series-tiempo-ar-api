#!coding=utf8
import json
from StringIO import StringIO

import unicodecsv

from series_tiempo_ar_api.apps.api.models import Catalog, Dataset, Distribution, Field
from series_tiempo_ar_api.apps.management.models import Node

HEADER_ROW = [
    'identifier', 'title', 'description', 'actualizado', 'indexable', 'discontinuado', 'error', 'error_mensaje'
]


def generate_attachments(queryset, get_indexable, get_present, get_error):
    out = StringIO()
    writer = unicodecsv.writer(out)

    writer.writerow(HEADER_ROW)

    for entity in queryset:
        meta = json.loads(entity.metadata)

        error, error_msg = get_error(entity)
        writer.writerow([
            entity.identifier if hasattr(entity, 'identifier') else entity.series_id,
            meta.get('title'),
            meta.get('description'),
            entity.updated,
            get_indexable(entity),
            get_present(entity),
            error,
            error_msg,
        ])
    out.seek(0)
    return out.read()


def generate_catalog_attachment(node=None):
    queryset = Catalog.objects.all()
    if node:
        queryset = queryset.filter(identifier=node.catalog_id)
    return generate_attachments(queryset,
                                lambda x: Node.objects.get(catalog_id=x.identifier).indexable,
                                lambda x: True,  # Catálogos no tiene concepto de discontinuado
                                lambda x: (x.error, ''))


def generate_dataset_attachment(node=None):
    queryset = Dataset.objects.all()
    if node:
        queryset = queryset.filter(catalog__identifier=node.catalog_id)

    return generate_attachments(queryset,
                                lambda x: x.indexable,
                                lambda x: x.available,
                                lambda x: (x.error, ''))


def generate_distribution_attachment(node=None):
    queryset = Distribution.objects.all()
    if node:
        queryset = queryset.filter(dataset__catalog__identifier=node.catalog_id)

    return generate_attachments(queryset,
                                lambda x: x.dataset.indexable,
                                lambda x: x.dataset.available,
                                lambda x: (bool(x.error), x.error))


def generate_field_attachment(node=None):
    queryset = Field.objects.all()
    if node:
        catalog = Catalog.objects.get(identifier=node.catalog_id)
        queryset = queryset.filter(distribution__dataset__catalog=catalog)

    return generate_attachments(queryset,
                                lambda x: x.distribution.dataset.indexable,
                                lambda x: x.distribution.dataset.available,
                                lambda x: (bool(x.distribution.error), x.distribution.error))
