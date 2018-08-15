#! coding: utf-8
from pydatajson import DataJson

from django_datajsonar.models import Catalog, Field, Distribution, Dataset
from series_tiempo_ar_api.apps.management.models import Indicator
from series_tiempo_ar_api.utils import get_available_fields


# pylint: disable=R0914
class IndicatorsGenerator(object):

    def __init__(self, node, task):
        self.node = node
        self.task = task
        # Shorthand!
        self.create = self.task.indicator_set.create

    def generate(self):
        node = self.node

        try:
            data_json = DataJson(node.catalog_url)
            data_json.get_fields(only_time_series=True)
            catalog = Catalog.objects.get(identifier=node.catalog_id)
        except Exception as e:
            self.task.info(self.task, "Error en la lectura del data.json de {}: {}".format(node.catalog_id, e))
            return

        self.calculate_catalog_indicators(node, catalog)
        self.calculate_series_indicators(node, data_json, catalog)
        self.calculate_distribution_indicators(node, data_json, catalog)
        self.calculate_dataset_indicators(node, data_json, catalog)

    def calculate_catalog_indicators(self, node, catalog):
        updated = catalog.updated
        self.create(type=Indicator.CATALOG_UPDATED, value=updated, node=node)
        self.create(type=Indicator.CATALOG_NOT_UPDATED, value=not updated, node=node)
        self.create(type=Indicator.CATALOG_TOTAL, value=1, node=node)

        error = catalog.error
        self.create(type=Indicator.CATALOG_ERROR, value=error, node=node)

    def calculate_dataset_indicators(self, node, data_json, catalog):
        indexable = Dataset.objects.filter(catalog=catalog, indexable=True)

        updated = indexable.filter(updated=True).count()
        self.create(type=Indicator.DATASET_UPDATED, value=updated, node=node)

        not_updated = indexable.filter(present=True).exclude(updated=True).count()
        self.create(type=Indicator.DATASET_NOT_UPDATED, value=not_updated, node=node)

        discontinued = indexable.filter(present=False).count()
        self.create(type=Indicator.DATASET_INDEXABLE_DISCONTINUED, value=discontinued, node=node)

        self.create(type=Indicator.DATASET_INDEXABLE, value=indexable.count(), node=node)

        error = Dataset.objects.filter(catalog=catalog, error=True).count()
        self.create(type=Indicator.DATASET_ERROR, value=error, node=node)

        not_indexable = Dataset.objects.filter(catalog=catalog, indexable=False)

        new = not_indexable.filter(new=True).count()
        self.create(type=Indicator.DATASET_NEW, value=new, node=node)

        not_indexable_discontinued = not_indexable.filter(present=False).count()
        self.create(type=Indicator.DATASET_NOT_INDEXABLE_DISCONTINUED,
                    value=not_indexable_discontinued,
                    node=node)

        not_indexable_previous = not_indexable.filter(new=False, present=True).count()
        self.create(type=Indicator.DATASET_NOT_INDEXABLE_PREVIOUS,
                    value=not_indexable_previous,
                    node=node)

        self.create(type=Indicator.DATASET_NOT_INDEXABLE, value=not_indexable.count(), node=node)

        available = len(data_json.get_datasets(only_time_series=True))
        self.create(type=Indicator.DATASET_AVAILABLE, value=available, node=node)

        total = get_available_fields().filter(distribution__dataset__catalog=catalog)\
            .values_list('distribution__dataset').distinct().count()
        self.create(type=Indicator.DATASET_TOTAL, value=total, node=node)

    def calculate_distribution_indicators(self, node, data_json, catalog):
        indexable = Distribution.objects.filter(dataset__catalog=catalog, dataset__indexable=True)

        updated = indexable.filter(updated=True).count()
        self.create(type=Indicator.DISTRIBUTION_UPDATED, value=updated, node=node)

        not_updated = indexable.filter(updated=False).count()
        self.create(type=Indicator.DISTRIBUTION_NOT_UPDATED, value=not_updated, node=node)

        discontinued = indexable.filter(present=False).count()
        self.create(type=Indicator.DISTRIBUTION_INDEXABLE_DISCONTINUED, value=discontinued, node=node)

        self.create(type=Indicator.DISTRIBUTION_INDEXABLE, value=indexable.count(), node=node)

        not_indexable = Distribution.objects.filter(dataset__catalog=catalog, dataset__indexable=False)

        new = not_indexable.filter(new=True).count()
        self.create(type=Indicator.DISTRIBUTION_NEW, value=new, node=node)

        previous = not_indexable.filter(new=False, present=True).count()
        self.create(type=Indicator.DISTRIBUTION_NOT_INDEXABLE_PREVIOUS, value=previous, node=node)

        error = Distribution.objects.filter(dataset__catalog=catalog, error=True).count()
        self.create(type=Indicator.DISTRIBUTION_ERROR, value=error, node=node)

        not_indexable_discontinued = not_indexable.filter(present=False).count()
        self.create(type=Indicator.DISTRIBUTION_NOT_INDEXABLE_DISCONTINUED,
                    value=not_indexable_discontinued,
                    node=node)

        self.create(type=Indicator.DISTRIBUTION_NOT_INDEXABLE, value=not_indexable.count(), node=node)

        self.create(type=Indicator.DISTRIBUTION_AVAILABLE,
                    value=len(data_json.get_distributions(only_time_series=True)),
                    node=node)

        self.create(type=Indicator.DISTRIBUTION_TOTAL,
                    value=get_available_fields().filter(distribution__dataset__catalog=catalog).
                    values_list('distribution').distinct().count(),
                    node=node)

    def calculate_series_indicators(self, node, data_json, catalog):
        fields = Field.objects.exclude(title='indice_tiempo')
        indexable = fields.filter(distribution__dataset__catalog=catalog,
                                  distribution__dataset__indexable=True)

        updated = indexable.filter(updated=True).count()
        self.create(type=Indicator.FIELD_UPDATED, value=updated, node=node)

        not_updated = indexable.filter(updated=False, present=True).count()
        self.create(type=Indicator.FIELD_NOT_UPDATED, value=not_updated, node=node)

        legacy_indexable = indexable.filter(present=False).count()
        self.create(type=Indicator.FIELD_INDEXABLE_DISCONTINUED, value=legacy_indexable, node=node)

        self.create(type=Indicator.FIELD_INDEXABLE, value=indexable.count(), node=node)

        not_indexable = fields.filter(distribution__dataset__catalog=catalog,
                                      distribution__dataset__indexable=False)

        new = not_indexable.filter(new=True).count()
        self.create(type=Indicator.FIELD_NEW, value=new, node=node)

        previous = not_indexable.filter(new=False, present=True).count()
        self.create(type=Indicator.FIELD_NOT_INDEXABLE_PREVIOUS, value=previous, node=node)

        error = Field.objects.filter(distribution__dataset__catalog=catalog, error=True).count()
        self.create(type=Indicator.FIELD_ERROR, value=error, node=node)

        not_indexable_discontinued = not_indexable.filter(present=False).count()
        self.create(type=Indicator.FIELD_NOT_INDEXABLE_DISCONTINUED,
                    value=not_indexable_discontinued,
                    node=node)

        self.create(type=Indicator.FIELD_NOT_INDEXABLE, value=not_indexable.count(), node=node)

        self.create(type=Indicator.FIELD_AVAILABLE,
                    value=len(data_json.get_fields(only_time_series=True)),
                    node=node)

        self.create(type=Indicator.FIELD_TOTAL,
                    value=get_available_fields().filter(distribution__dataset__catalog=catalog).count(),
                    node=node)
