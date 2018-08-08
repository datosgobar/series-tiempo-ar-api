# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django_datajsonar.models import Metadata

def migrate_enhanced_meta(apps, schema_editor):
    Metadata = apps.get_model('django_datajsonar', 'Metadata')
    db_alias = schema_editor.connection.alias

    name_changes = {
        'index_start': 'time_index_start',
        'index_end': 'time_index_end',
        'periodicity': 'frequency',
        'index_size': 'time_index_size',
        'days_since_last_update': 'days_without_data',
    }

    models_to_change = Metadata.objects.using(db_alias).filter(key__in=name_changes.keys())
    new_models = []
    for meta in models_to_change:
        new_models.append(Metadata(
            key=name_changes[meta.key],
            value=meta.value,
            object_id=meta.object_id,
            content_type=meta.content_type,
        ))

    models_to_change.delete()
    Metadata.objects.bulk_create(new_models)


class Migration(migrations.Migration):
    dependencies = [
        ('metadata', '0002_catalogalias'),
    ]

    operations = [
        migrations.RunPython(migrate_enhanced_meta)
    ]
