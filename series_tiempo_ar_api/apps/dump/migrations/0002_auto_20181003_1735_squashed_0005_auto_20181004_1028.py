# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-10-08 14:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import minio_storage.storage
import series_tiempo_ar_api.apps.dump.models


class Migration(migrations.Migration):

    dependencies = [
        ('django_datajsonar', '0012_auto_20180831_1020'),
        ('dump', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dumpfile',
            name='file_type',
            field=models.CharField(choices=[('xlsx', 'XLSX'), ('zip', 'ZIP'), ('csv', 'CSV')], default='csv', max_length=12),
        ),
        migrations.AddField(
            model_name='dumpfile',
            name='node',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='django_datajsonar.Node'),
        ),
        migrations.AlterField(
            model_name='dumpfile',
            name='file',
            field=models.FileField(storage=minio_storage.storage.MinioMediaStorage(), upload_to=series_tiempo_ar_api.apps.dump.models.dumpfile_upload_to),
        ),
        migrations.AlterField(
            model_name='dumpfile',
            name='file_name',
            field=models.CharField(max_length=64),
        ),
    ]
