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


def migrate_files(apps, schema_editor):
    IndexingTaskCron = apps.get_model('django_datajsonar', 'Metadata')
    db_alias = schema_editor.connection.alias

    IndexingTaskCron.objects.using(db_alias).all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('management', 'migrate_files_to_minio'),
    ]

    operations = [
        migrations.RunPython(migrate_files, reverse_code=lambda x, y: None)
    ]
