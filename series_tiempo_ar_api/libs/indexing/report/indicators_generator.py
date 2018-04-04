#! coding: utf-8
import json

from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.models import Catalog, Field, Distribution, Dataset
from series_tiempo_ar_api.apps.management.models import Indicator


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

    def calculate_series_indicators(self, node, data_json):
        fields_total = len(data_json.get_fields(only_time_series=True))
        self.create(type=Indicator.FIELD_TOTAL, value=fields_total, node=node)

        catalog = Catalog.objects.get(identifier=node.catalog_id)

        indexable = Field.objects.filter(distribution__dataset__catalog=catalog,
                                         distribution__dataset__indexable=True).count()
        self.create(type=Indicator.FIELD_INDEXABLE, value=indexable, node=node)

        not_indexable = Field.objects.filter(distribution__dataset__catalog=catalog,
                                             distribution__dataset__indexable=False,
                                             distribution__dataset__present=True).count()
        self.create(type=Indicator.FIELD_NOT_INDEXABLE, value=not_indexable, node=node)

        # Indicador ya persistido anteriormente, no se llama a create
        updated = self.task.indicator_set.get_or_create(type=Indicator.FIELD_UPDATED,
                                                        node=node)[0].value

        not_updated = indexable - updated
        self.create(type=Indicator.FIELD_NOT_UPDATED,
                    value=not_updated,
                    node=node)

    def calculate_distribution_indicators(self, node, data_json):
        catalog = Catalog.objects.get(identifier=node.catalog_id)

        distribution_total = len(data_json.get_distributions(only_time_series=True))
        self.create(type=Indicator.DISTRIBUTION_TOTAL, value=distribution_total, node=node)

        indexable = Distribution.objects.filter(dataset__catalog=catalog,
                                                dataset__indexable=True).count()
        self.create(type=Indicator.DISTRIBUTION_INDEXABLE, value=indexable, node=node)

        not_indexable = Distribution.objects.filter(dataset__catalog=catalog,
                                                    dataset__indexable=False,
                                                    dataset__present=True).count()
        self.create(type=Indicator.DISTRIBUTION_NOT_INDEXABLE, value=not_indexable, node=node)

        updated = self.task.indicator_set.get_or_create(type=Indicator.DISTRIBUTION_UPDATED,
                                                        node=node)[0].value

        not_updated = indexable - updated
        self.create(type=Indicator.DISTRIBUTION_NOT_UPDATED, value=not_updated, node=node)

    def calculate_dataset_indicators(self, node, data_json):
        dataset_total = len(data_json.get_datasets(only_time_series=True))
        self.create(type=Indicator.DATASET_TOTAL, value=dataset_total, node=node)

        catalog = Catalog.objects.get(identifier=node.catalog_id)

        indexable = Dataset.objects.filter(catalog=catalog, indexable=True).count()
        self.create(type=Indicator.DATASET_INDEXABLE, value=indexable, node=node)

        not_indexable = Dataset.objects.filter(catalog=catalog, indexable=False).count()
        self.create(type=Indicator.DATASET_NOT_INDEXABLE,
                    value=not_indexable,
                    node=node)

        updated = Dataset.objects.filter(catalog=catalog, updated=True).count()
        self.create(type=Indicator.DATASET_UPDATED, value=updated, node=node)

        not_updated = indexable - updated
        self.create(type=Indicator.DATASET_NOT_UPDATED,
                    value=not_updated,
                    node=node)

        error = Dataset.objects.filter(catalog=catalog, error=True).count()
        self.create(type=Indicator.DATASET_ERROR, value=error, node=node)
