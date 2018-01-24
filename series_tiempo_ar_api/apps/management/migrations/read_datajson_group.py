#! coding: utf-8

from django.conf import settings
from django.db import migrations
from django.contrib.auth.models import Group


def create_group(*_):
    Group.objects.get_or_create(name=settings.READ_DATAJSON_RECIPIENT_GROUP)


def delete_group(*_):
    Group.objects.filter(name=settings.READ_DATAJSON_RECIPIENT_GROUP).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('management', '0012_readdatajsontask_stats'),
    ]

    operations = [
        migrations.RunPython(create_group, delete_group),
    ]
