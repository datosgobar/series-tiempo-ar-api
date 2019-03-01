from django.contrib.contenttypes.models import ContentType
from django_datajsonar.models import Field, Metadata

from series_tiempo_ar_api.apps.management import meta_keys


def get_available_series(*args, **kwargs):
    field_content_type = ContentType.objects.get_for_model(Field)
    available_fields = Metadata.objects.filter(
        key=meta_keys.AVAILABLE,
        value='true',
        content_type=field_content_type).values_list('object_id', flat=True)
    fields = Field.objects.filter(
        id__in=available_fields,
        present=True,
        error=False,
    ).filter(*args, **kwargs)
    return fields
