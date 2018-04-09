#!coding=utf8
import json
from StringIO import StringIO

import unicodecsv

from series_tiempo_ar_api.apps.api.models import Catalog
from series_tiempo_ar_api.apps.management.models import Node

HEADER_ROW = [
    'identifier', 'title', 'description', 'actualizado', 'indexable', 'discontinuado', 'error', 'error_mensaje'
]


def generate_attachments():
    out = StringIO()
    writer = unicodecsv.writer(out)

    writer.writerow(HEADER_ROW)
    for catalog in Catalog.objects.all():
        node = Node.objects.get(catalog_id=catalog.identifier)
        meta = json.loads(catalog.metadata)
        writer.writerow([
            catalog.identifier,
            meta.get('title'),
            meta.get('description'),
            catalog.updated,
            node.indexable,
            catalog.error,
            '',
        ])
    out.seek(0)
    return out.read()
