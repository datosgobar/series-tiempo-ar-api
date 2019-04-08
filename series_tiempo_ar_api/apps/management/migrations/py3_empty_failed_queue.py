#! coding: utf-8
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('management', '0016_auto_20180406_0916'),
    ]
    operations = [
        migrations.RunPython(lambda x, y: None),
    ]
