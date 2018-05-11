#!coding=utf8

from django_datajsonar.models import Field, Metadata


def get_available_fields():
    available_ids = Metadata.objects.filter(
        key='available',
        content_type__model='field'
    ).values_list('object_id')
    return Field.objects.filter(id__in=available_ids).exclude(title='indice_tiempo')
