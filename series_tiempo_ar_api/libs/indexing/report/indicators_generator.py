#! coding: utf-8
import json

from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.models import Catalog, Field, Distribution, Dataset
from series_tiempo_ar_api.apps.management.models import Indicator


# pylint: disable=R0914
class IndicatorsGenerator(object):

    def __init__(self, node, task):
        self.node = node
        self.task = task
        # Shorthand!
        self.create = self.task.indicator_set.create

    def generate(self):
        node = self.node

        self.calculate_catalog_indicators(node)
        data_json = DataJson(json.loads(node.catalog))

        self.calculate_series_indicators(node, data_json)
        self.calculate_distribution_indicators(node, data_json)
        self.calculate_dataset_indicators(node, data_json)

    def calculate_catalog_indicators(self, node):
        catalog_model = Catalog.objects.get(identifier=node.catalog_id)
        updated = catalog_model.updated
        self.create(type=Indicator.CATALOG_UPDATED, value=updated, node=node)
        self.create(type=Indicator.CATALOG_NOT_UPDATED, value=not updated, node=node)
        self.create(type=Indicator.CATALOG_TOTAL, value=1, node=node)

        error = catalog_model.error
        self.create(type=Indicator.CATALOG_ERROR, value=error, node=node)

    def calculate_dataset_indicators(self, node, data_json):
        catalog = Catalog.objects.get(identifier=node.catalog_id)

        indexable = Dataset.objects.filter(catalog=catalog, indexable=True)

        updated = indexable.filter(updated=True).count()
        self.create(type=Indicator.DATASET_UPDATED, value=updated, node=node)

        not_updated = indexable.filter(present=True).exclude(updated=True).count()
        self.create(type=Indicator.DATASET_NOT_UPDATED, value=not_updated, node=node)

        legacy_indexable = indexable.filter(present=False).count()
        self.create(type=Indicator.DATASET_INDEXABLE_DISCONTINUED, value=legacy_indexable, node=node)

        self.create(type=Indicator.DATASET_INDEXABLE, value=indexable.count(), node=node)

        error = Dataset.objects.filter(catalog=catalog, error=True).count()
        self.create(type=Indicator.DATASET_ERROR, value=error, node=node)

        not_indexable = Dataset.objects.filter(catalog=catalog, indexable=False)

        new = self.task.indicator_set.filter(node=node, type=Indicator.DATASET_NEW)
        new = new[0].value if new else 0
        not_indexable_discontinued = not_indexable.filter(present=False).count()
        self.create(type=Indicator.DATASET_NOT_INDEXABLE_DISCONTINUED,
                    value=not_indexable_discontinued,
                    node=node)

        not_indexable_previous = not_indexable.count() - new - not_indexable_discontinued
        self.create(type=Indicator.DATASET_NOT_INDEXABLE_PREVIOUS,
                    value=not_indexable_previous,
                    node=node)

        self.create(type=Indicator.DATASET_NOT_INDEXABLE, value=not_indexable.count(), node=node)

        available = len(data_json.get_datasets(only_time_series=True))
        self.create(type=Indicator.DATASET_AVAILABLE, value=available, node=node)

        total = Field.objects.filter(distribution__dataset__catalog=catalog)\
            .values_list('distribution__dataset').distinct().count()
        self.create(type=Indicator.DATASET_TOTAL, value=total, node=node)

    def calculate_distribution_indicators(self, node, data_json):
        catalog = Catalog.objects.get(identifier=node.catalog_id)

        indexable = Distribution.objects.filter(dataset__catalog=catalog, dataset__indexable=True)

        not_updated = indexable.filter(dataset__present=True).exclude(updated=True)
        self.create(type=Indicator.DISTRIBUTION_INDEXABLE, value=indexable.count(), node=node)

        not_indexable = Dataset.objects.filter(catalog=catalog, indexable=False, present=True)
        not_indexable_ids = not_indexable.values_list('identifier', flat=True)
        not_indexable_previous = 0
        no_longer_present = 0
        for dataset in data_json['dataset']:
            if dataset.get('identifier') in not_indexable_ids:
                not_indexable_previous += len(dataset.get('distribution', []))

            ids = [dist.get('identifier') for dist in dataset.get('distribution', [])]
            for dist in not_updated.filter(dataset__identifier=dataset.get('identifier')):
                if dist.identifier not in ids:
                    no_longer_present += 1

        self.create(type=Indicator.DISTRIBUTION_NOT_UPDATED,
                    value=not_updated.count() - no_longer_present,
                    node=node)

        legacy_indexable = indexable.filter(dataset__present=False).count() + no_longer_present
        self.create(type=Indicator.DISTRIBUTION_INDEXABLE_DISCONTINUED, value=legacy_indexable, node=node)

        new = self.task.indicator_set.filter(node=node, type=Indicator.DISTRIBUTION_NEW)
        new = new[0].value if new else 0

        self.create(type=Indicator.DISTRIBUTION_NOT_INDEXABLE_PREVIOUS,
                    value=not_indexable_previous,
                    node=node)

        not_indexable_discontinued = Distribution.objects.filter(dataset__indexable=False,
                                                                 dataset__present=False).count()
        self.create(type=Indicator.DISTRIBUTION_NOT_INDEXABLE_DISCONTINUED,
                    value=not_indexable_discontinued,
                    node=node)

        not_indexable_total = new + not_indexable_previous + not_indexable_discontinued
        self.create(type=Indicator.DISTRIBUTION_NOT_INDEXABLE, value=not_indexable_total, node=node)

        self.create(type=Indicator.DISTRIBUTION_AVAILABLE,
                    value=len(data_json.get_distributions(only_time_series=True)),
                    node=node)

        self.create(type=Indicator.DISTRIBUTION_TOTAL,
                    value=Field.objects.filter(distribution__dataset__catalog=catalog).
                    values_list('distribution').distinct().count(),
                    node=node)

    def calculate_series_indicators(self, node, data_json):
        catalog = Catalog.objects.get(identifier=node.catalog_id)

        indexable = Field.objects.filter(distribution__dataset__catalog=catalog, distribution__dataset__indexable=True)

        not_updated = indexable.filter(distribution__dataset__present=True)\
            .exclude(distribution__dataset__updated=True).count()
        self.create(type=Indicator.FIELD_NOT_UPDATED, value=not_updated, node=node)

        legacy_indexable = indexable.filter(distribution__dataset__present=False).count()

        updated_models = indexable.filter(distribution__dataset__present=True,
                                          distribution__dataset__updated=True).count()
        updated_real = self.task.indicator_set.filter(type=Indicator.FIELD_UPDATED)
        updated_real = updated_real[0].value if updated_real else 0
        legacy_indexable += updated_models - updated_real

        self.create(type=Indicator.FIELD_INDEXABLE_DISCONTINUED, value=legacy_indexable, node=node)

        self.create(type=Indicator.FIELD_INDEXABLE, value=indexable.count(), node=node)

        not_indexable = Dataset.objects.filter(catalog=catalog, indexable=False)

        new = self.task.indicator_set.filter(node=node, type=Indicator.FIELD_NEW)
        new = new[0].value if new else 0

        not_indexable_ids = not_indexable.values_list('identifier', flat=True)
        not_indexable_previous = 0
        for dataset in data_json.get('dataset', []):
            if dataset.get('identifier') in not_indexable_ids:
                for distribution in dataset.get('distribution', []):
                    # Sumo todos menos el time index (-1)
                    not_indexable_previous += len(distribution.get('field', [])) - 1

        self.create(type=Indicator.FIELD_NOT_INDEXABLE_PREVIOUS,
                    value=not_indexable_previous,
                    node=node)

        not_indexable_discontinued = not_indexable.filter(distribution__dataset__present=False).count()
        self.create(type=Indicator.FIELD_NOT_INDEXABLE_DISCONTINUED,
                    value=not_indexable_discontinued,
                    node=node)

        not_indexable = not_indexable_previous + new + not_indexable_discontinued
        self.create(type=Indicator.FIELD_NOT_INDEXABLE, value=not_indexable, node=node)

        self.create(type=Indicator.FIELD_AVAILABLE,
                    value=len(data_json.get_fields(only_time_series=True)),
                    node=node)

        self.create(type=Indicator.FIELD_TOTAL,
                    value=Field.objects.filter(distribution__dataset__catalog=catalog).count(),
                    node=node)
