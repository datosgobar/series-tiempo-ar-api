import json

from django_datajsonar.models import Distribution, Field, Node

from series_tiempo_ar_api.libs.indexing import constants


class DistributionRepository:

    def __init__(self, instance: Distribution):
        self.instance = instance

    def get_time_index_series(self):
        fields = self.instance.field_set.all()
        for field in fields:
            meta = json.loads(field.metadata)
            if meta.get(constants.SPECIAL_TYPE) == constants.TIME_INDEX:
                return field

        msg = f"No se encontró un índice de tiempo para la distribución: {self.instance.identifier}"
        raise Field.DoesNotExist(msg)

    def get_node(self):
        return Node.objects.get(catalog_id=self.instance.dataset.catalog.identifier)
