# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-05 12:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_auto_20180104_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='present',
            field=models.BooleanField(default=True),
        ),
    ]
