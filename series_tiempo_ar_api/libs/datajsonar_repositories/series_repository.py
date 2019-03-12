from django.contrib.contenttypes.models import ContentType
from django_datajsonar.models import Field, Metadata

from series_tiempo_ar_api.apps.management import meta_keys


class SeriesRepository:

    @staticmethod
    def get_available_series(*args, **kwargs):
        field_content_type = ContentType.objects.get_for_model(Field)
        available_fields = Metadata.objects.filter(
            key=meta_keys.AVAILABLE,
            value='true',
            content_type=field_content_type).values_list('object_id', flat=True)
        fields = SeriesRepository.get_present_series(*args, **kwargs)\
            .filter(id__in=available_fields)
        return fields

    @staticmethod
    def get_present_series(*args, **kwargs):
        return Field.objects.filter(present=True, error=False, *args, **kwargs)
