#!coding=utf8
from __future__ import unicode_literals

from django.db import migrations


def move(*_):
    """NoOP mantenida por legacy reasons"""


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0002_auto_20180510_1709'),
        ('api', '0034_distribution_error'),
        ('django_datajsonar', '0002_auto_20180507_1752'),
    ]

    operations = [
        migrations.RunPython(move)
    ]
