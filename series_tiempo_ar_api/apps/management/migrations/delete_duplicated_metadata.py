# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-02-08 18:09
from __future__ import unicode_literals

from django.db import migrations


# No op mantenida para consistencia
def delete_all_but_last_periodicity(*_):
    pass


def revert(*_):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_auto_20190208_1509'),
        ('contenttypes', '0001_initial'),
        ('django_datajsonar', '0020_auto_20190131_1213')
    ]

    operations = [
        migrations.RunPython(delete_all_but_last_periodicity, revert)
    ]
