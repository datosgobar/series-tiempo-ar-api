#!coding=utf8
from __future__ import unicode_literals

from django.db import migrations, models
import django_datajsonar.models as djar_models
import series_tiempo_ar_api.apps.management.models as mgmt_models


def assign_nodes(apps, *_):
    indics = apps.get_model('management', 'Indicator').objects.all()
    node_model = apps.get_model('django_datajsonar', 'Node')

    for indic in indics:
        node = node_model.objects.get(catalog_id=indic.node.catalog_id)
        indic.node_tmp = node
        indic.save()


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0002_auto_20180510_1709'),
    ]

    operations = [
        migrations.RunPython(assign_nodes),
    ]
