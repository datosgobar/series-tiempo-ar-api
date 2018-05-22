#!coding=utf8

from django_datajsonar.models import Field, Metadata

from series_tiempo_ar_api.apps.management import meta_keys


def get_available_fields():
    available_ids = Metadata.objects.filter(
        key=meta_keys.AVAILABLE,
        content_type__model='field'
    ).values_list('object_id')
    return Field.objects.filter(id__in=available_ids).exclude(title='indice_tiempo')
