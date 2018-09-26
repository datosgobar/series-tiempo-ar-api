# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.db import migrations
from django.core.files import File
from minio_storage.errors import MinIOError


def migrate_files(apps, schema_editor):
    Distribution = apps.get_model('django_datajsonar', 'Distribution')
    db_alias = schema_editor.connection.alias

    for distribution in Distribution.objects.using(db_alias).all():
        try:
            if distribution.data_file:
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
        migrations.RunPython(migrate_files)
    ]
