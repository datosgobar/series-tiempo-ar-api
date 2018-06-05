#!coding=utf8
from __future__ import unicode_literals

from django.db import migrations, models
import django_datajsonar.models as djar_models
import series_tiempo_ar_api.apps.management.models as mgmt_models


class Migration(migrations.Migration):

    dependencies = [
        ('management', 'move_indicators_to_datajsonar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indicator',
            name='node',
        ),
        migrations.RenameField(
            model_name='indicator',
            old_name='node_tmp',
            new_name='node',
        )
    ]


