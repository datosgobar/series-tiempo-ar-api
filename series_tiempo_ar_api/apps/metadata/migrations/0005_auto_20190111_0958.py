# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-01-11 12:58
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0004_auto_20181219_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadataconfig',
            name='query_config',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={'dataset_description': {'boost': 1}, 'dataset_source': {'boost': 1}, 'dataset_title': {'boost': 1}, 'description': {'boost': 1.5}}),
        ),
    ]
