#! coding: utf-8

from django.conf import settings
from django.db import migrations
from django.contrib.auth.models import Group


ERROR_MSG = 'error_msg'


def delete(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    Metadata = apps.get_model('django_datajsonar', 'Metadata')

    Metadata.objects.using(db_alias).filter(key=ERROR_MSG).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('management', '0005_auto_20180813_1510'),
    ]

    operations = [
        migrations.RunPython(delete),
    ]

