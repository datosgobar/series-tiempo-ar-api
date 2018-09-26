# -*- coding: utf-8 -*-
"""Esta migración no va a funcionar a futuro si pasamos a dejar usar el storage de minio
Debería borrarse en el caso que el storage no sea más minio!
"""
from __future__ import unicode_literals

import os

from django.conf import settings
from django.db import migrations
from django.core.files import File
from minio_storage.errors import MinIOError
from minio_storage.storage import MinioMediaStorage

from django_datajsonar.models import Distribution


def migrate_files(*_):
    for distribution in Distribution.objects.all():
        try:
            if distribution.data_file:
                assert distribution.data_file.storage.__class__ == MinioMediaStorage
                distribution.data_file.read()
        except MinIOError:
            # El file no está en minio, intentamos leerlo desde el fs
            with open(os.path.join(settings.MEDIA_ROOT, distribution.data_file.name), 'rb') as f:
                distribution.data_file = File(f)
                distribution.save()


class Migration(migrations.Migration):

    dependencies = [
        ('management', 'remove_error_msg_enhanced_meta'),
    ]

    operations = [
        migrations.RunPython(migrate_files, reverse_code=lambda x, y: None)
    ]
