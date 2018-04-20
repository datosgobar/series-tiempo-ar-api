#! coding: utf-8
from django.db import migrations
from django_rq import get_failed_queue


class Migration(migrations.Migration):
    dependencies = [
        ('management', '0016_auto_20180406_0916'),
    ]
    operations = [
        migrations.RunPython(lambda x, y: get_failed_queue().empty()),
    ]
