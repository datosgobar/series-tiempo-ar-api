import json

from django_datajsonar.models import Field, Distribution

from series_tiempo_ar_api.libs.indexing import constants


def get_distribution_time_index(distribution: Distribution) -> Field:
    fields = distribution.field_set.filter(present=True)
    for field in fields:
        meta = json.loads(field.metadata)
        if meta.get(constants.SPECIAL_TYPE) == constants.TIME_INDEX:
            return field

    raise Field.DoesNotExist
