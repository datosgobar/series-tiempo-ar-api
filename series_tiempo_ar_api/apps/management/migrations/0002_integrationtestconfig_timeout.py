# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-08-26 15:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_auto_20190613_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='integrationtestconfig',
            name='timeout',
            field=models.IntegerField(default=1000),
        ),
    ]
