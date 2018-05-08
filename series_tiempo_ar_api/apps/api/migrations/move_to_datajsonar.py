#!coding=utf8
from __future__ import unicode_literals

from django.db import migrations, models
import django_datajsonar.models
import series_tiempo_ar_api.apps.api.models as api_models


def move(*_):
    django_datajsonar.models.Catalog.objects.all().delete()
    for catalog in api_models.Catalog.objects.all():
        django_datajsonar.models.Catalog.objects.get_or_create(
            title=catalog.title,
            identifier=catalog.identifier,
            metadata=catalog.metadata,
        )

    django_datajsonar.models.Dataset.objects.all().delete()
    for dataset in api_models.Dataset.objects.all():
        django_datajsonar.models.Dataset.objects.get_or_create(
            title="",
            identifier=dataset.identifier,
            catalog=django_datajsonar.models.Catalog.objects.get(identifier=dataset.catalog.identifier),
            metadata=dataset.metadata,
            indexable=dataset.indexable,
        )

    django_datajsonar.models.Distribution.objects.all().delete()
    for distribution in api_models.Distribution.objects.all():
        django_datajsonar.models.Distribution.objects.get_or_create(
            identifier=distribution.identifier,
            metadata=distribution.metadata,
            dataset=django_datajsonar.models.Dataset.objects.get(identifier=distribution.dataset.identifier),
            download_url=distribution.download_url,
            data_hash=distribution.data_hash,
            data_file=distribution.data_file
        )

    django_datajsonar.models.Field.objects.all().delete()
    for field in api_models.Field.objects.all():
        django_datajsonar.models.Field.objects.get_or_create(
            title=field.title,
            identifier=field.series_id,
            metadata=field.metadata,
            distribution=django_datajsonar.models.Distribution.objects.get(identifier=field.distribution.identifier),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_distribution_error'),
        ('django_datajsonar', '__latest__'),
    ]

    operations = [
        migrations.RunPython(move)
    ]
